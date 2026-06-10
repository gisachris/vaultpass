import uuid
import asyncio
from datetime import datetime, timezone, timedelta
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from vaultpass_backend.main import app
from vaultpass_backend.models.document import DocumentType, Document
from vaultpass_backend.models.document_share import DocumentShare
from vaultpass_backend.models.user import User
from vaultpass_backend.services.document_access_service import DocumentAccessService

client = TestClient(app)

@pytest.fixture
def mock_user():
    return User(
        id=uuid.uuid4(),
        full_name="Jane Doe",
        email="jane@example.com",
        password_hash="hashed_password"
    )

@pytest.fixture
def override_auth_dependency(mock_user):
    from vaultpass_backend.core.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.pop(get_current_user, None)

def test_service_resolve_document_access_owner(mock_user):
    doc_id = uuid.uuid4()
    doc = Document(id=doc_id, owner_id=mock_user.id, title="Test Doc")

    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = doc
    mock_db.execute.return_value = mock_res

    res_doc, share = asyncio.run(
        DocumentAccessService.resolve_document_access(mock_db, doc_id, mock_user.id)
    )
    assert res_doc == doc
    assert share is None

def test_service_resolve_document_access_share(mock_user):
    doc_id = uuid.uuid4()
    recipient_id = uuid.uuid4()
    doc = Document(id=doc_id, owner_id=mock_user.id, title="Test Doc")
    share = DocumentShare(
        id=uuid.uuid4(),
        document_id=doc_id,
        recipient_user_id=recipient_id,
        is_active=True,
        expires_at=None
    )

    mock_db = AsyncMock()
    
    # We execute twice in resolve_document_access:
    # 1. doc query
    # 2. share query
    mock_res_doc = MagicMock()
    mock_res_doc.scalar_one_or_none.return_value = doc

    mock_res_share = MagicMock()
    mock_res_share.scalar_one_or_none.return_value = share

    mock_db.execute.side_effect = [mock_res_doc, mock_res_share]

    res_doc, res_share = asyncio.run(
        DocumentAccessService.resolve_document_access(mock_db, doc_id, recipient_id)
    )
    assert res_doc == doc
    assert res_share == share

def test_service_resolve_document_access_expired(mock_user):
    from fastapi import HTTPException
    doc_id = uuid.uuid4()
    recipient_id = uuid.uuid4()
    doc = Document(id=doc_id, owner_id=mock_user.id, title="Test Doc")
    expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
    share = DocumentShare(
        id=uuid.uuid4(),
        document_id=doc_id,
        recipient_user_id=recipient_id,
        is_active=True,
        expires_at=expired_time
    )

    mock_db = AsyncMock()
    mock_res_doc = MagicMock()
    mock_res_doc.scalar_one_or_none.return_value = doc
    mock_res_share = MagicMock()
    mock_res_share.scalar_one_or_none.return_value = share
    mock_db.execute.side_effect = [mock_res_doc, mock_res_share]

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            DocumentAccessService.resolve_document_access(mock_db, doc_id, recipient_id)
        )
    assert exc.value.status_code == status.HTTP_410_GONE

@patch("vaultpass_backend.services.document_access_service.storage_service.generate_signed_url", new_callable=AsyncMock)
@patch("vaultpass_backend.services.document_access_service.AuditService.log_action", new_callable=AsyncMock)
def test_service_generate_preview_url_owner(mock_log, mock_gen_url, mock_user):
    doc_id = uuid.uuid4()
    doc = Document(id=doc_id, owner_id=mock_user.id, title="Test Doc", file_path="path/to/file", mime_type="application/pdf", file_name="file.pdf")

    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = doc
    mock_db.execute.return_value = mock_res

    mock_gen_url.return_value = "https://signed.url"

    res = asyncio.run(
        DocumentAccessService.generate_preview_url(mock_db, doc_id, mock_user.id)
    )
    assert res["preview_url"] == "https://signed.url"
    assert res["file_name"] == "file.pdf"
    mock_log.assert_called_once()

@patch("vaultpass_backend.api.documents.DocumentAccessService.generate_preview_url", new_callable=AsyncMock)
def test_router_preview_endpoint(mock_gen_preview, override_auth_dependency):
    doc_id = uuid.uuid4()
    mock_gen_preview.return_value = {
        "document_id": doc_id,
        "file_name": "test.pdf",
        "file_type": "application/pdf",
        "preview_url": "https://signed.url/preview",
        "expires_at": "2026-06-10T12:00:00Z"
    }

    response = client.get(f"/api/documents/{doc_id}/preview")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert data["data"]["preview_url"] == "https://signed.url/preview"
