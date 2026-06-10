import uuid
from datetime import datetime, timezone
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from vaultpass_backend.main import app
from vaultpass_backend.models.document import DocumentType, Document
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

def test_upload_document_validation_invalid_type(override_auth_dependency):
    files = {"file": ("test.txt", b"dummy content", "text/plain")}
    data = {
        "title": "My Text File",
        "document_type": "PASSPORT",
        "description": "Unsupported upload test"
    }
    
    response = client.post("/api/documents/upload", files=files, data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid file extension" in response.json()["detail"]

def test_upload_document_validation_oversized(override_auth_dependency):
    oversized_content = b"0" * (10 * 1024 * 1024 + 1)
    files = {"file": ("test.pdf", oversized_content, "application/pdf")}
    data = {
        "title": "Big PDF",
        "document_type": "PASSPORT"
    }
    
    response = client.post("/api/documents/upload", files=files, data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "exceeds maximum limit" in response.json()["detail"]

@patch("vaultpass_backend.services.notification.NotificationService.notify_document_uploaded", new_callable=AsyncMock)
@patch("vaultpass_backend.services.document_service.storage_service.upload_file", new_callable=AsyncMock)
def test_service_upload_document_success(mock_upload, mock_notify_uploaded, mock_user):
    from vaultpass_backend.services.document_service import upload_document
    import asyncio
    
    # Mock FastAPI UploadFile
    mock_file = MagicMock()
    mock_file.filename = "passport.pdf"
    mock_file.content_type = "application/pdf"
    
    # Mock the seek and tell for file size validation
    mock_file.file.tell.return_value = 1024
    
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    
    async def run_test():
        return await upload_document(
            db=mock_db,
            owner_id=mock_user.id,
            file=mock_file,
            title="My Passport",
            document_type=DocumentType.PASSPORT,
            description="Passport doc",
            expiry_date=None
        )
        
    doc = asyncio.run(run_test())
    
    assert doc.title == "My Passport"
    assert doc.owner_id == mock_user.id
    assert doc.file_name == "passport.pdf"
    mock_upload.assert_called_once()
    # db.add is now called for both the Document and the AuditLog, so assert
    # that a Document instance was among the added objects.
    added_types = [type(call.args[0]).__name__ for call in mock_db.add.call_args_list]
    assert "Document" in added_types
    mock_db.commit.assert_called_once()

@patch("vaultpass_backend.api.documents.upload_document", new_callable=AsyncMock)
def test_router_upload_success(mock_upload_document, override_auth_dependency, mock_user):
    expected_id = uuid.uuid4()
    
    mock_doc = MagicMock(spec=Document)
    mock_doc.id = expected_id
    mock_doc.owner_id = mock_user.id
    mock_doc.title = "My Passport"
    mock_doc.document_type = DocumentType.PASSPORT
    mock_doc.description = "Passport info"
    mock_doc.file_name = "passport.pdf"
    mock_doc.file_path = f"{mock_user.id}/{expected_id}_passport.pdf"
    mock_doc.file_size = 1234
    mock_doc.mime_type = "application/pdf"
    mock_doc.expiry_date = None
    mock_doc.uploaded_at = datetime.now(timezone.utc)
    mock_doc.created_at = datetime.now(timezone.utc)
    mock_doc.updated_at = None
    
    mock_upload_document.return_value = mock_doc
    
    files = {"file": ("passport.pdf", b"pdf content", "application/pdf")}
    data = {
        "title": "My Passport",
        "document_type": "PASSPORT",
        "description": "Passport info"
    }
    
    response = client.post("/api/documents/upload", files=files, data=data)
    assert response.status_code == status.HTTP_201_CREATED
    res_data = response.json()
    assert res_data["title"] == "My Passport"
    assert res_data["document_type"] == "PASSPORT"
    assert res_data["id"] == str(expected_id)

@patch("vaultpass_backend.api.documents.get_documents", new_callable=AsyncMock)
def test_router_list_documents(mock_get_documents, override_auth_dependency, mock_user):
    mock_doc = MagicMock(spec=Document)
    mock_doc.id = uuid.uuid4()
    mock_doc.owner_id = mock_user.id
    mock_doc.title = "Doc 1"
    mock_doc.document_type = DocumentType.PASSPORT
    mock_doc.description = "Some description"
    mock_doc.file_name = "doc1.pdf"
    mock_doc.file_path = "p1"
    mock_doc.file_size = 10
    mock_doc.mime_type = "application/pdf"
    mock_doc.expiry_date = None
    mock_doc.uploaded_at = datetime.now(timezone.utc)
    mock_doc.created_at = datetime.now(timezone.utc)
    mock_doc.updated_at = None

    mock_get_documents.return_value = ([mock_doc], 1)
    
    response = client.get("/api/documents?page=1&limit=10&search=Doc")
    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()
    assert res_data["total"] == 1
    assert len(res_data["items"]) == 1
    assert res_data["items"][0]["title"] == "Doc 1"

@patch("vaultpass_backend.api.documents.get_document_by_id", new_callable=AsyncMock)
def test_router_get_details(mock_get_doc, override_auth_dependency, mock_user):
    doc_id = uuid.uuid4()
    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = mock_user.id
    mock_doc.title = "My Passport"
    mock_doc.document_type = DocumentType.PASSPORT
    mock_doc.description = None
    mock_doc.file_name = "passport.pdf"
    mock_doc.file_path = "p1"
    mock_doc.file_size = 10
    mock_doc.mime_type = "application/pdf"
    mock_doc.expiry_date = None
    mock_doc.uploaded_at = datetime.now(timezone.utc)
    mock_doc.created_at = datetime.now(timezone.utc)
    mock_doc.updated_at = None
    
    mock_get_doc.return_value = mock_doc
    
    response = client.get(f"/api/documents/{doc_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(doc_id)

@patch("vaultpass_backend.api.documents.DocumentAccessService.generate_download_url", new_callable=AsyncMock)
def test_router_download(mock_gen_url, override_auth_dependency):
    doc_id = uuid.uuid4()
    mock_gen_url.return_value = {
        "document_id": doc_id,
        "file_name": "test.pdf",
        "download_url": "https://example.com/signed-url",
        "expires_at": "2026-06-10T12:00:00Z"
    }
    
    response = client.get(f"/api/documents/{doc_id}/download")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True
    assert response.json()["data"]["download_url"] == "https://example.com/signed-url"

@patch("vaultpass_backend.api.documents.update_document", new_callable=AsyncMock)
def test_router_update(mock_update_doc, override_auth_dependency, mock_user):
    doc_id = uuid.uuid4()
    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = mock_user.id
    mock_doc.title = "Updated Title"
    mock_doc.document_type = DocumentType.WILL
    mock_doc.description = "Updated desc"
    mock_doc.file_name = "will.pdf"
    mock_doc.file_path = "p1"
    mock_doc.file_size = 10
    mock_doc.mime_type = "application/pdf"
    mock_doc.expiry_date = None
    mock_doc.uploaded_at = datetime.now(timezone.utc)
    mock_doc.created_at = datetime.now(timezone.utc)
    mock_doc.updated_at = datetime.now(timezone.utc)
    
    mock_update_doc.return_value = mock_doc
    
    payload = {
        "title": "Updated Title",
        "document_type": "WILL"
    }
    
    response = client.put(f"/api/documents/{doc_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Updated Title"
    assert response.json()["document_type"] == "WILL"

@patch("vaultpass_backend.api.documents.delete_document", new_callable=AsyncMock)
def test_router_delete(mock_delete, override_auth_dependency):
    doc_id = uuid.uuid4()
    mock_delete.return_value = None
    
    response = client.delete(f"/api/documents/{doc_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Document deleted successfully"

@patch("vaultpass_backend.services.document_service.select")
def test_service_get_document_by_id_success(mock_select, mock_user):
    from vaultpass_backend.services.document_service import get_document_by_id
    import asyncio
    
    doc_id = uuid.uuid4()
    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = mock_user.id
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_doc
    mock_db.execute.return_value = mock_result
    
    async def run_test():
        return await get_document_by_id(mock_db, doc_id, mock_user.id)
        
    doc = asyncio.run(run_test())
    assert doc == mock_doc

def test_service_get_document_by_id_not_found(mock_user):
    from vaultpass_backend.services.document_service import get_document_by_id
    from fastapi import HTTPException
    import asyncio
    
    doc_id = uuid.uuid4()
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    async def run_test():
        await get_document_by_id(mock_db, doc_id, mock_user.id)
        
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())
        
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Document not found" in exc_info.value.detail

def test_service_get_document_by_id_forbidden(mock_user):
    from vaultpass_backend.services.document_service import get_document_by_id
    from fastapi import HTTPException
    import asyncio
    
    doc_id = uuid.uuid4()
    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = uuid.uuid4() # Different user
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_doc
    mock_db.execute.return_value = mock_result
    
    async def run_test():
        await get_document_by_id(mock_db, doc_id, mock_user.id)
        
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())
        
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Not authorized to access this document" in exc_info.value.detail

def test_service_get_documents_success(mock_user):
    from vaultpass_backend.services.document_service import get_documents
    import asyncio
    
    mock_db = AsyncMock()
    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 1
    
    mock_doc = MagicMock(spec=Document)
    mock_doc.owner_id = mock_user.id
    
    mock_items_result = MagicMock()
    mock_items_result.scalars.return_value.all.return_value = [mock_doc]
    
    # First execute call is for count query, second is for items query
    mock_db.execute.side_effect = [mock_count_result, mock_items_result]
    
    async def run_test():
        return await get_documents(mock_db, mock_user.id, page=1, limit=10, search="test")
        
    items, total = asyncio.run(run_test())
    assert items == [mock_doc]
    assert total == 1

@patch("vaultpass_backend.services.notification.NotificationService.notify_document_updated", new_callable=AsyncMock)
def test_service_update_document_success(mock_notify_updated, mock_user):
    from vaultpass_backend.services.document_service import update_document
    from vaultpass_backend.schemas.document import DocumentUpdateRequest
    import asyncio
    
    doc_id = uuid.uuid4()
    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = mock_user.id
    mock_doc.title = "Old Title"
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_doc
    mock_db.execute.return_value = mock_result
    
    update_data = DocumentUpdateRequest(title="New Title")
    
    async def run_test():
        return await update_document(mock_db, doc_id, mock_user.id, update_data)
        
    updated_doc = asyncio.run(run_test())
    assert updated_doc.title == "New Title"
    mock_db.commit.assert_called_once()

@patch("vaultpass_backend.services.notification.NotificationService.notify_document_deleted", new_callable=AsyncMock)
@patch("vaultpass_backend.services.document_service.storage_service.delete_file", new_callable=AsyncMock)
def test_service_delete_document_success(mock_delete_file, mock_notify_deleted, mock_user):
    from vaultpass_backend.services.document_service import delete_document
    import asyncio
    
    doc_id = uuid.uuid4()
    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = mock_user.id
    mock_doc.file_path = "p1"
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_doc
    mock_db.execute.return_value = mock_result
    
    async def run_test():
        await delete_document(mock_db, doc_id, mock_user.id)
        
    asyncio.run(run_test())
    mock_delete_file.assert_called_once_with("p1")
    mock_db.delete.assert_called_once_with(mock_doc)
    mock_db.commit.assert_called_once()

@patch("vaultpass_backend.services.document_service.storage_service.generate_signed_url", new_callable=AsyncMock)
def test_service_generate_download_link_success(mock_gen_url, mock_user):
    from vaultpass_backend.services.document_service import generate_download_link
    import asyncio
    
    doc_id = uuid.uuid4()
    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = mock_user.id
    mock_doc.file_path = "p1"
    
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_doc
    mock_db.execute.return_value = mock_result
    
    mock_gen_url.return_value = "https://example.com/signed-url"
    
    async def run_test():
        return await generate_download_link(mock_db, doc_id, mock_user.id)
        
    url = asyncio.run(run_test())
    assert url == "https://example.com/signed-url"
    mock_gen_url.assert_called_once_with("p1", expires_in_seconds=3600)

@patch("vaultpass_backend.api.documents.get_document_by_id", new_callable=AsyncMock)
def test_router_get_details_not_found(mock_get_doc, override_auth_dependency):
    from fastapi import HTTPException
    mock_get_doc.side_effect = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    doc_id = uuid.uuid4()
    response = client.get(f"/api/documents/{doc_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Document not found" in response.json()["detail"]

@patch("vaultpass_backend.api.documents.get_document_by_id", new_callable=AsyncMock)
def test_router_get_details_forbidden(mock_get_doc, override_auth_dependency):
    from fastapi import HTTPException
    mock_get_doc.side_effect = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this document")
    
    doc_id = uuid.uuid4()
    response = client.get(f"/api/documents/{doc_id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Not authorized to access this document" in response.json()["detail"]
