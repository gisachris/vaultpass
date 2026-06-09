import uuid
from datetime import datetime, timezone, timedelta
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from vaultpass_backend.main import app
from vaultpass_backend.models.document_share import DocumentShare
from vaultpass_backend.models.document import Document, DocumentType
from vaultpass_backend.models.trusted_contact import TrustedContact
from vaultpass_backend.models.user import User

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

# ================= ROUTER TESTS =================

@patch("vaultpass_backend.api.document_shares.DocumentShareService.create_share", new_callable=AsyncMock)
def test_router_create_share_success(mock_create_share, override_auth_dependency, mock_user):
    share_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    contact_id = uuid.uuid4()

    mock_share = MagicMock(spec=DocumentShare)
    mock_share.id = share_id
    mock_share.document_id = doc_id
    mock_share.contact_id = contact_id
    mock_share.owner_id = mock_user.id
    mock_share.access_token = "secure_token"
    mock_share.share_link = "https://vaultpass.app/shared/secure_token"
    mock_share.is_active = True
    mock_share.recipient_user_id = None
    mock_share.expires_at = None
    mock_share.last_accessed_at = None
    mock_share.created_at = datetime.now(timezone.utc)
    mock_share.updated_at = None

    mock_create_share.return_value = mock_share

    payload = {
        "document_id": str(doc_id),
        "contact_id": str(contact_id),
        "expires_at": None
    }

    response = client.post("/api/v1/shares", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    res_data = response.json()
    assert res_data["id"] == str(share_id)
    assert res_data["access_token"] == "secure_token"
    assert "share_link" in res_data

@patch("vaultpass_backend.api.document_shares.DocumentShareService.get_my_shares", new_callable=AsyncMock)
def test_router_list_shares(mock_get_my_shares, override_auth_dependency, mock_user):
    mock_share = MagicMock(spec=DocumentShare)
    mock_share.id = uuid.uuid4()
    mock_share.document_id = uuid.uuid4()
    mock_share.contact_id = uuid.uuid4()
    mock_share.owner_id = mock_user.id
    mock_share.access_token = "token"
    mock_share.share_link = "https://vaultpass.app/shared/token"
    mock_share.is_active = True
    mock_share.recipient_user_id = None
    mock_share.expires_at = None
    mock_share.last_accessed_at = None
    mock_share.created_at = datetime.now(timezone.utc)
    mock_share.updated_at = None

    mock_get_my_shares.return_value = [mock_share]

    response = client.get("/api/v1/shares")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["access_token"] == "token"

@patch("vaultpass_backend.api.document_shares.DocumentShareService.get_share_by_id", new_callable=AsyncMock)
def test_router_get_share_details(mock_get_share, override_auth_dependency, mock_user):
    share_id = uuid.uuid4()
    mock_share = MagicMock(spec=DocumentShare)
    mock_share.id = share_id
    mock_share.document_id = uuid.uuid4()
    mock_share.contact_id = uuid.uuid4()
    mock_share.owner_id = mock_user.id
    mock_share.access_token = "token"
    mock_share.share_link = "https://vaultpass.app/shared/token"
    mock_share.is_active = True
    mock_share.recipient_user_id = None
    mock_share.expires_at = None
    mock_share.last_accessed_at = None
    mock_share.created_at = datetime.now(timezone.utc)
    mock_share.updated_at = None

    mock_get_share.return_value = mock_share

    response = client.get(f"/api/v1/shares/{share_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(share_id)

@patch("vaultpass_backend.api.document_shares.DocumentShareService.update_share", new_callable=AsyncMock)
def test_router_update_share(mock_update, override_auth_dependency, mock_user):
    share_id = uuid.uuid4()
    mock_share = MagicMock(spec=DocumentShare)
    mock_share.id = share_id
    mock_share.document_id = uuid.uuid4()
    mock_share.contact_id = uuid.uuid4()
    mock_share.owner_id = mock_user.id
    mock_share.access_token = "token"
    mock_share.share_link = "https://vaultpass.app/shared/token"
    mock_share.is_active = False
    mock_share.recipient_user_id = None
    mock_share.expires_at = datetime.now(timezone.utc)
    mock_share.last_accessed_at = None
    mock_share.created_at = datetime.now(timezone.utc)
    mock_share.updated_at = datetime.now(timezone.utc)

    mock_update.return_value = mock_share

    payload = {
        "is_active": False
    }

    response = client.put(f"/api/v1/shares/{share_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_active"] is False

@patch("vaultpass_backend.api.document_shares.DocumentShareService.revoke_share", new_callable=AsyncMock)
def test_router_revoke_share(mock_revoke, override_auth_dependency, mock_user):
    share_id = uuid.uuid4()
    mock_share = MagicMock(spec=DocumentShare)
    mock_share.id = share_id
    mock_share.document_id = uuid.uuid4()
    mock_share.contact_id = uuid.uuid4()
    mock_share.owner_id = mock_user.id
    mock_share.access_token = "token"
    mock_share.share_link = "https://vaultpass.app/shared/token"
    mock_share.is_active = False
    mock_share.recipient_user_id = None
    mock_share.expires_at = None
    mock_share.last_accessed_at = None
    mock_share.created_at = datetime.now(timezone.utc)
    mock_share.updated_at = None

    mock_revoke.return_value = mock_share

    response = client.patch(f"/api/v1/shares/{share_id}/revoke")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_active"] is False

@patch("vaultpass_backend.api.document_shares.DocumentShareService.activate_share", new_callable=AsyncMock)
def test_router_activate_share(mock_activate, override_auth_dependency, mock_user):
    share_id = uuid.uuid4()
    mock_share = MagicMock(spec=DocumentShare)
    mock_share.id = share_id
    mock_share.document_id = uuid.uuid4()
    mock_share.contact_id = uuid.uuid4()
    mock_share.owner_id = mock_user.id
    mock_share.access_token = "token"
    mock_share.share_link = "https://vaultpass.app/shared/token"
    mock_share.is_active = True
    mock_share.recipient_user_id = None
    mock_share.expires_at = None
    mock_share.last_accessed_at = None
    mock_share.created_at = datetime.now(timezone.utc)
    mock_share.updated_at = None

    mock_activate.return_value = mock_share

    response = client.patch(f"/api/v1/shares/{share_id}/activate")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_active"] is True

@patch("vaultpass_backend.api.document_shares.DocumentShareService.delete_share", new_callable=AsyncMock)
def test_router_delete_share(mock_delete, override_auth_dependency):
    share_id = uuid.uuid4()
    mock_delete.return_value = None

    response = client.delete(f"/api/v1/shares/{share_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Document share deleted successfully"

@patch("vaultpass_backend.api.document_shares.DocumentShareService.get_shares_for_document", new_callable=AsyncMock)
def test_router_list_shares_for_document(mock_get_shares, override_auth_dependency, mock_user):
    doc_id = uuid.uuid4()
    mock_share = MagicMock(spec=DocumentShare)
    mock_share.id = uuid.uuid4()
    mock_share.document_id = doc_id
    mock_share.contact_id = uuid.uuid4()
    mock_share.owner_id = mock_user.id
    mock_share.access_token = "token"
    mock_share.share_link = "https://vaultpass.app/shared/token"
    mock_share.is_active = True
    mock_share.recipient_user_id = None
    mock_share.expires_at = None
    mock_share.last_accessed_at = None
    mock_share.created_at = datetime.now(timezone.utc)
    mock_share.updated_at = None

    mock_get_shares.return_value = [mock_share]

    response = client.get(f"/api/v1/shares/document/{doc_id}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["document_id"] == str(doc_id)

@patch("vaultpass_backend.api.document_shares.DocumentShareService.get_public_share_by_token", new_callable=AsyncMock)
def test_router_get_public_share(mock_get_public):
    mock_metadata = {
        "title": "My Passport",
        "document_type": DocumentType.PASSPORT,
        "created_at": datetime.now(timezone.utc),
        "expiry_date": None,
        "download_url": "https://example.com/signed-url"
    }
    mock_get_public.return_value = mock_metadata

    response = client.get("/public/share/token123")
    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()
    assert res_data["title"] == "My Passport"
    assert res_data["document_type"] == "PASSPORT"
    assert res_data["download_url"] == "https://example.com/signed-url"
    assert "owner_id" not in res_data # Verify private data is hidden


# ================= SERVICE LAYER TESTS =================

@patch("vaultpass_backend.services.notification.NotificationService.notify_document_shared", new_callable=AsyncMock)
@patch("vaultpass_backend.services.document_share.select")
def test_service_create_share_success(mock_select, mock_notify_shared, mock_user):
    from vaultpass_backend.services.document_share import DocumentShareService
    from vaultpass_backend.schemas.document_share import CreateDocumentShareRequest
    from vaultpass_backend.repository.document_share import DocumentShareRepository
    import asyncio

    doc_id = uuid.uuid4()
    contact_id = uuid.uuid4()

    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = mock_user.id

    mock_contact = MagicMock(spec=TrustedContact)
    mock_contact.id = contact_id
    mock_contact.owner_id = mock_user.id
    mock_contact.linked_user_id = None  # external contact — forces external share path

    mock_db = AsyncMock()
    mock_doc_result = MagicMock()
    mock_doc_result.scalar_one_or_none.return_value = mock_doc
    mock_contact_result = MagicMock()
    mock_contact_result.scalar_one_or_none.return_value = mock_contact

    mock_db.execute.side_effect = [mock_doc_result, mock_contact_result]

    share_data = CreateDocumentShareRequest(
        document_id=doc_id,
        contact_id=contact_id,
        expires_at=None
    )

    # Mock repository call
    mock_share_saved = MagicMock(spec=DocumentShare)
    mock_share_saved.id = uuid.uuid4()

    async def run_test():
        with patch.object(DocumentShareRepository, "create_share", new_callable=AsyncMock) as mock_repo_create:
            mock_repo_create.return_value = mock_share_saved
            return await DocumentShareService.create_share(mock_db, mock_user.id, share_data)

    res = asyncio.run(run_test())
    assert res == mock_share_saved

@patch("vaultpass_backend.services.document_share.select")
def test_service_create_share_unauthorized_document(mock_select, mock_user):
    from vaultpass_backend.services.document_share import DocumentShareService
    from vaultpass_backend.schemas.document_share import CreateDocumentShareRequest
    from fastapi import HTTPException
    import asyncio

    doc_id = uuid.uuid4()
    contact_id = uuid.uuid4()

    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = uuid.uuid4() # Different user ID (unauthorized)

    mock_db = AsyncMock()
    mock_doc_result = MagicMock()
    mock_doc_result.scalar_one_or_none.return_value = mock_doc

    mock_db.execute.return_value = mock_doc_result

    share_data = CreateDocumentShareRequest(
        document_id=doc_id,
        contact_id=contact_id,
        expires_at=None
    )

    async def run_test():
        await DocumentShareService.create_share(mock_db, mock_user.id, share_data)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Not authorized to access this document" in exc_info.value.detail

@patch("vaultpass_backend.services.document_share.select")
def test_service_create_share_unauthorized_contact(mock_select, mock_user):
    from vaultpass_backend.services.document_share import DocumentShareService
    from vaultpass_backend.schemas.document_share import CreateDocumentShareRequest
    from fastapi import HTTPException
    import asyncio

    doc_id = uuid.uuid4()
    contact_id = uuid.uuid4()

    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = mock_user.id

    mock_contact = MagicMock(spec=TrustedContact)
    mock_contact.id = contact_id
    mock_contact.owner_id = uuid.uuid4() # Different user ID (unauthorized)

    mock_db = AsyncMock()
    mock_doc_result = MagicMock()
    mock_doc_result.scalar_one_or_none.return_value = mock_doc
    mock_contact_result = MagicMock()
    mock_contact_result.scalar_one_or_none.return_value = mock_contact

    mock_db.execute.side_effect = [mock_doc_result, mock_contact_result]

    share_data = CreateDocumentShareRequest(
        document_id=doc_id,
        contact_id=contact_id,
        expires_at=None
    )

    async def run_test():
        await DocumentShareService.create_share(mock_db, mock_user.id, share_data)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Not authorized to access this trusted contact" in exc_info.value.detail

@patch("vaultpass_backend.services.document_share.DocumentShareRepository.get_share_by_token", new_callable=AsyncMock)
def test_service_get_public_share_expired(mock_get_token):
    from vaultpass_backend.services.document_share import DocumentShareService
    from fastapi import HTTPException
    import asyncio

    share_id = uuid.uuid4()
    mock_share = MagicMock(spec=DocumentShare)
    mock_share.id = share_id
    mock_share.is_active = True
    # Expired 1 hour ago
    mock_share.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)

    mock_get_token.return_value = mock_share
    mock_db = AsyncMock()

    async def run_test():
        await DocumentShareService.get_public_share_by_token(mock_db, "expired_token")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "link has expired" in exc_info.value.detail

@patch("vaultpass_backend.services.document_share.DocumentShareRepository.get_share_by_token", new_callable=AsyncMock)
def test_service_get_public_share_inactive(mock_get_token):
    from vaultpass_backend.services.document_share import DocumentShareService
    from fastapi import HTTPException
    import asyncio

    share_id = uuid.uuid4()
    mock_share = MagicMock(spec=DocumentShare)
    mock_share.id = share_id
    mock_share.is_active = False
    mock_share.expires_at = None

    mock_get_token.return_value = mock_share
    mock_db = AsyncMock()

    async def run_test():
        await DocumentShareService.get_public_share_by_token(mock_db, "inactive_token")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "link has been deactivated" in exc_info.value.detail


# ================= INTERNAL / EXTERNAL SHARE TESTS =================

@patch("vaultpass_backend.services.notification.NotificationService.notify_internal_share_received", new_callable=AsyncMock)
@patch("vaultpass_backend.services.document_share.select")
def test_service_create_internal_share(mock_select, mock_notify_internal, mock_user):
    """When a contact has linked_user_id set, an internal share is created and recipient is notified."""
    from vaultpass_backend.services.document_share import DocumentShareService
    from vaultpass_backend.schemas.document_share import CreateDocumentShareRequest
    from vaultpass_backend.repository.document_share import DocumentShareRepository
    import asyncio

    doc_id = uuid.uuid4()
    contact_id = uuid.uuid4()
    recipient_id = uuid.uuid4()

    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = mock_user.id
    mock_doc.title = "Passport.pdf"

    mock_contact = MagicMock(spec=TrustedContact)
    mock_contact.id = contact_id
    mock_contact.owner_id = mock_user.id
    mock_contact.full_name = "Jane Smith"
    mock_contact.linked_user_id = recipient_id  # internal contact

    mock_owner = MagicMock(spec=User)
    mock_owner.full_name = mock_user.full_name

    mock_db = AsyncMock()
    doc_result = MagicMock(); doc_result.scalar_one_or_none.return_value = mock_doc
    contact_result = MagicMock(); contact_result.scalar_one_or_none.return_value = mock_contact
    owner_result = MagicMock(); owner_result.scalar_one_or_none.return_value = mock_owner
    mock_db.execute.side_effect = [doc_result, contact_result, owner_result]

    saved_share = MagicMock(spec=DocumentShare)
    saved_share.id = uuid.uuid4()
    saved_share.recipient_user_id = recipient_id

    share_data = CreateDocumentShareRequest(document_id=doc_id, contact_id=contact_id)

    async def run_test():
        with patch.object(DocumentShareRepository, "create_share", new_callable=AsyncMock) as mock_repo_create:
            mock_repo_create.return_value = saved_share
            return await DocumentShareService.create_share(mock_db, mock_user.id, share_data)

    result = asyncio.run(run_test())
    assert result == saved_share
    # Recipient notification must have been sent
    mock_notify_internal.assert_called_once()
    call_kwargs = mock_notify_internal.call_args.kwargs
    assert call_kwargs["recipient_user_id"] == recipient_id
    assert "Passport.pdf" in call_kwargs["doc_title"]


@patch("vaultpass_backend.services.notification.NotificationService.notify_document_shared", new_callable=AsyncMock)
@patch("vaultpass_backend.services.document_share.select")
def test_service_create_external_share_unchanged(mock_select, mock_notify_shared, mock_user):
    """When a contact has no linked_user_id, the existing external share flow is used."""
    from vaultpass_backend.services.document_share import DocumentShareService
    from vaultpass_backend.schemas.document_share import CreateDocumentShareRequest
    from vaultpass_backend.repository.document_share import DocumentShareRepository
    import asyncio

    doc_id = uuid.uuid4()
    contact_id = uuid.uuid4()

    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = mock_user.id
    mock_doc.title = "Insurance.pdf"

    mock_contact = MagicMock(spec=TrustedContact)
    mock_contact.id = contact_id
    mock_contact.owner_id = mock_user.id
    mock_contact.full_name = "Mom"
    mock_contact.linked_user_id = None  # external contact

    mock_db = AsyncMock()
    doc_result = MagicMock(); doc_result.scalar_one_or_none.return_value = mock_doc
    contact_result = MagicMock(); contact_result.scalar_one_or_none.return_value = mock_contact
    mock_db.execute.side_effect = [doc_result, contact_result]

    saved_share = MagicMock(spec=DocumentShare)
    saved_share.id = uuid.uuid4()
    saved_share.recipient_user_id = None

    share_data = CreateDocumentShareRequest(document_id=doc_id, contact_id=contact_id)

    async def run_test():
        with patch.object(DocumentShareRepository, "create_share", new_callable=AsyncMock) as mock_repo_create:
            mock_repo_create.return_value = saved_share
            return await DocumentShareService.create_share(mock_db, mock_user.id, share_data)

    result = asyncio.run(run_test())
    assert result == saved_share
    # Original notification must have been sent (not the internal one)
    mock_notify_shared.assert_called_once()


# ================= SHARED-WITH-ME ENDPOINT TESTS =================

@patch("vaultpass_backend.api.document_shares.DocumentShareService.get_shared_with_me", new_callable=AsyncMock)
def test_router_shared_with_me_list(mock_get_swm, override_auth_dependency, mock_user):
    """GET /api/v1/shares/shared-with-me returns 200 with a list of received shares."""
    from vaultpass_backend.schemas.document_share import SharedWithMeResponse

    share_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    mock_swm = SharedWithMeResponse(
        share_id=share_id,
        document_id=doc_id,
        document_title="Passport.pdf",
        document_type="PASSPORT",
        owner_name="John Doe",
        shared_at=now,
        expires_at=None,
        is_active=True,
    )
    mock_get_swm.return_value = [mock_swm]

    response = client.get("/api/v1/shares/shared-with-me")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["document_title"] == "Passport.pdf"
    assert data[0]["owner_name"] == "John Doe"
    assert data[0]["share_id"] == str(share_id)


@patch("vaultpass_backend.api.document_shares.DocumentShareService.get_shared_with_me_detail", new_callable=AsyncMock)
def test_router_shared_with_me_detail(mock_get_detail, override_auth_dependency, mock_user):
    """GET /api/v1/shares/shared-with-me/{id} returns 200 with full detail."""
    from vaultpass_backend.schemas.document_share import SharedWithMeDetailResponse

    share_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    owner_id = uuid.uuid4()
    contact_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    mock_detail = SharedWithMeDetailResponse(
        share_id=share_id,
        document_id=doc_id,
        document_title="Insurance.pdf",
        document_type="INSURANCE",
        owner_name="John Doe",
        owner_id=owner_id,
        contact_id=contact_id,
        shared_at=now,
        expires_at=None,
        is_active=True,
        last_accessed_at=None,
    )
    mock_get_detail.return_value = mock_detail

    response = client.get(f"/api/v1/shares/shared-with-me/{share_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["document_title"] == "Insurance.pdf"
    assert data["owner_id"] == str(owner_id)
    assert data["contact_id"] == str(contact_id)


@patch("vaultpass_backend.api.document_shares.DocumentShareService.get_shared_with_me_detail", new_callable=AsyncMock)
def test_router_shared_with_me_unauthorized_blocked(mock_get_detail, override_auth_dependency):
    """If the share does not belong to the current user, the service raises 404."""
    from fastapi import HTTPException

    share_id = uuid.uuid4()
    mock_get_detail.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Shared document not found or you are not the recipient"
    )

    response = client.get(f"/api/v1/shares/shared-with-me/{share_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "recipient" in response.json()["detail"]
