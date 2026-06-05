import uuid
from datetime import datetime, timezone
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from vaultpass_backend.main import app
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

# ================= API ROUTER TESTS =================

@patch("vaultpass_backend.api.trusted_contacts.TrustedContactService.create_contact", new_callable=AsyncMock)
def test_router_create_contact_success(mock_create, override_auth_dependency, mock_user):
    contact_id = uuid.uuid4()
    mock_contact = MagicMock(spec=TrustedContact)
    mock_contact.id = contact_id
    mock_contact.owner_id = mock_user.id
    mock_contact.full_name = "John Doe"
    mock_contact.email = "john@gmail.com"
    mock_contact.phone_number = "+250788000000"
    mock_contact.relationship = "Brother"
    mock_contact.notes = "Emergency contact"
    mock_contact.created_at = datetime.now(timezone.utc)
    mock_contact.updated_at = None

    mock_create.return_value = mock_contact

    payload = {
        "full_name": "John Doe",
        "email": "john@gmail.com",
        "phone_number": "+250788000000",
        "relationship": "Brother",
        "notes": "Emergency contact"
    }

    response = client.post("/api/v1/trusted-contacts", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    res_data = response.json()
    assert res_data["message"] == "Trusted contact created successfully"
    assert res_data["data"]["id"] == str(contact_id)
    assert res_data["data"]["email"] == "john@gmail.com"
    assert res_data["data"]["full_name"] == "John Doe"

def test_router_create_contact_validation_errors(override_auth_dependency):
    # Test min length for full name
    payload = {
        "full_name": "J",
        "email": "invalid-email",
        "relationship": "Friend"
    }
    response = client.post("/api/v1/trusted-contacts", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test relationship length limit (over 100 characters)
    payload_long_relationship = {
        "full_name": "John Doe",
        "email": "john@gmail.com",
        "relationship": "F" * 101
    }
    response = client.post("/api/v1/trusted-contacts", json=payload_long_relationship)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@patch("vaultpass_backend.api.trusted_contacts.TrustedContactService.list_contacts", new_callable=AsyncMock)
def test_router_list_contacts(mock_list, override_auth_dependency, mock_user):
    mock_contact = MagicMock(spec=TrustedContact)
    mock_contact.id = uuid.uuid4()
    mock_contact.owner_id = mock_user.id
    mock_contact.full_name = "John Doe"
    mock_contact.email = "john@gmail.com"
    mock_contact.phone_number = None
    mock_contact.relationship = "Brother"
    mock_contact.notes = None
    mock_contact.created_at = datetime.now(timezone.utc)
    mock_contact.updated_at = None

    mock_list.return_value = ([mock_contact], 1)

    response = client.get("/api/v1/trusted-contacts?page=1&page_size=10")
    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()
    assert res_data["total"] == 1
    assert len(res_data["items"]) == 1
    assert res_data["items"][0]["full_name"] == "John Doe"

@patch("vaultpass_backend.api.trusted_contacts.TrustedContactService.search_contacts", new_callable=AsyncMock)
def test_router_search_contacts(mock_search, override_auth_dependency, mock_user):
    mock_contact = MagicMock(spec=TrustedContact)
    mock_contact.id = uuid.uuid4()
    mock_contact.owner_id = mock_user.id
    mock_contact.full_name = "John Doe"
    mock_contact.email = "john@gmail.com"
    mock_contact.phone_number = None
    mock_contact.relationship = "Brother"
    mock_contact.notes = None
    mock_contact.created_at = datetime.now(timezone.utc)
    mock_contact.updated_at = None

    mock_search.return_value = ([mock_contact], 1)

    response = client.get("/api/v1/trusted-contacts/search?q=john&page=1&page_size=10")
    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()
    assert res_data["total"] == 1
    assert len(res_data["items"]) == 1
    assert res_data["items"][0]["full_name"] == "John Doe"

@patch("vaultpass_backend.api.trusted_contacts.TrustedContactService.get_contact_by_id", new_callable=AsyncMock)
def test_router_get_single_contact(mock_get, override_auth_dependency, mock_user):
    contact_id = uuid.uuid4()
    mock_contact = MagicMock(spec=TrustedContact)
    mock_contact.id = contact_id
    mock_contact.owner_id = mock_user.id
    mock_contact.full_name = "John Doe"
    mock_contact.email = "john@gmail.com"
    mock_contact.phone_number = None
    mock_contact.relationship = "Brother"
    mock_contact.notes = None
    mock_contact.created_at = datetime.now(timezone.utc)
    mock_contact.updated_at = None

    mock_get.return_value = mock_contact

    response = client.get(f"/api/v1/trusted-contacts/{contact_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(contact_id)

@patch("vaultpass_backend.api.trusted_contacts.TrustedContactService.update_contact", new_callable=AsyncMock)
def test_router_update_contact(mock_update, override_auth_dependency, mock_user):
    contact_id = uuid.uuid4()
    mock_contact = MagicMock(spec=TrustedContact)
    mock_contact.id = contact_id
    mock_contact.owner_id = mock_user.id
    mock_contact.full_name = "John Updated"
    mock_contact.email = "john@gmail.com"
    mock_contact.phone_number = None
    mock_contact.relationship = "Brother"
    mock_contact.notes = "Updated notes"
    mock_contact.created_at = datetime.now(timezone.utc)
    mock_contact.updated_at = datetime.now(timezone.utc)

    mock_update.return_value = mock_contact

    payload = {
        "full_name": "John Updated",
        "notes": "Updated notes"
    }

    response = client.patch(f"/api/v1/trusted-contacts/{contact_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == "John Updated"
    assert response.json()["notes"] == "Updated notes"

@patch("vaultpass_backend.api.trusted_contacts.TrustedContactService.delete_contact", new_callable=AsyncMock)
def test_router_delete_contact(mock_delete, override_auth_dependency):
    contact_id = uuid.uuid4()
    mock_delete.return_value = None

    response = client.delete(f"/api/v1/trusted-contacts/{contact_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Trusted contact deleted successfully"


# ================= SERVICE LAYER TESTS =================

@patch("vaultpass_backend.services.notification.NotificationService.notify_contact_added", new_callable=AsyncMock)
@patch("vaultpass_backend.services.trusted_contact.TrustedContactRepository.get_contact_by_email", new_callable=AsyncMock)
@patch("vaultpass_backend.services.trusted_contact.TrustedContactRepository.create_contact", new_callable=AsyncMock)
def test_service_create_contact_success(mock_create, mock_get_email, mock_notify, mock_user):
    from vaultpass_backend.services.trusted_contact import TrustedContactService
    from vaultpass_backend.schemas.trusted_contact import TrustedContactCreate
    import asyncio

    mock_get_email.return_value = None
    
    mock_db = AsyncMock()
    contact_data = TrustedContactCreate(
        full_name="Sarah Doe",
        email="sarah@gmail.com",
        relationship="Sister"
    )

    async def run_test():
        return await TrustedContactService.create_contact(mock_db, mock_user.id, contact_data)

    asyncio.run(run_test())
    mock_get_email.assert_called_once_with(db=mock_db, email="sarah@gmail.com", owner_id=mock_user.id)
    mock_create.assert_called_once()

@patch("vaultpass_backend.services.trusted_contact.TrustedContactRepository.get_contact_by_email", new_callable=AsyncMock)
def test_service_create_contact_duplicate_conflict(mock_get_email, mock_user):
    from vaultpass_backend.services.trusted_contact import TrustedContactService
    from vaultpass_backend.schemas.trusted_contact import TrustedContactCreate
    from fastapi import HTTPException
    import asyncio

    existing_contact = MagicMock(spec=TrustedContact)
    mock_get_email.return_value = existing_contact
    
    mock_db = AsyncMock()
    contact_data = TrustedContactCreate(
        full_name="Sarah Doe",
        email="sarah@gmail.com",
        relationship="Sister"
    )

    async def run_test():
        await TrustedContactService.create_contact(mock_db, mock_user.id, contact_data)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())
        
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in exc_info.value.detail

@patch("vaultpass_backend.services.trusted_contact.TrustedContactRepository.get_contact_by_id", new_callable=AsyncMock)
def test_service_get_contact_by_id_not_found(mock_get_id, mock_user):
    from vaultpass_backend.services.trusted_contact import TrustedContactService
    from fastapi import HTTPException
    import asyncio

    mock_get_id.return_value = None
    mock_db = AsyncMock()
    contact_id = uuid.uuid4()

    async def run_test():
        await TrustedContactService.get_contact_by_id(mock_db, contact_id, mock_user.id)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Trusted contact not found" in exc_info.value.detail

@patch("vaultpass_backend.services.trusted_contact.TrustedContactRepository.get_contact_by_id", new_callable=AsyncMock)
def test_service_get_contact_by_id_forbidden(mock_get_id, mock_user):
    from vaultpass_backend.services.trusted_contact import TrustedContactService
    from fastapi import HTTPException
    import asyncio

    mock_contact = MagicMock(spec=TrustedContact)
    mock_contact.owner_id = uuid.uuid4() # Different user ID

    mock_get_id.return_value = mock_contact
    mock_db = AsyncMock()
    contact_id = uuid.uuid4()

    async def run_test():
        await TrustedContactService.get_contact_by_id(mock_db, contact_id, mock_user.id)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Not authorized" in exc_info.value.detail

@patch("vaultpass_backend.services.trusted_contact.TrustedContactRepository.get_contact_by_id", new_callable=AsyncMock)
@patch("vaultpass_backend.services.trusted_contact.TrustedContactRepository.update_contact", new_callable=AsyncMock)
@patch("vaultpass_backend.services.trusted_contact.TrustedContactRepository.get_contact_by_email", new_callable=AsyncMock)
def test_service_update_contact_duplicate_conflict(mock_get_email, mock_update, mock_get_id, mock_user):
    from vaultpass_backend.services.trusted_contact import TrustedContactService
    from vaultpass_backend.schemas.trusted_contact import TrustedContactUpdate
    from fastapi import HTTPException
    import asyncio

    contact_id = uuid.uuid4()
    mock_contact = MagicMock(spec=TrustedContact)
    mock_contact.id = contact_id
    mock_contact.owner_id = mock_user.id
    mock_contact.email = "old@gmail.com"

    mock_get_id.return_value = mock_contact

    # Mock that another contact already owns the new email
    another_contact = MagicMock(spec=TrustedContact)
    another_contact.id = uuid.uuid4() # Different UUID
    mock_get_email.return_value = another_contact

    mock_db = AsyncMock()
    update_data = TrustedContactUpdate(email="new@gmail.com")

    async def run_test():
        await TrustedContactService.update_contact(mock_db, contact_id, mock_user.id, update_data)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in exc_info.value.detail

@patch("vaultpass_backend.services.notification.NotificationService.notify_contact_deleted", new_callable=AsyncMock)
@patch("vaultpass_backend.services.trusted_contact.TrustedContactRepository.get_contact_by_id", new_callable=AsyncMock)
@patch("vaultpass_backend.services.trusted_contact.TrustedContactRepository.delete_contact", new_callable=AsyncMock)
def test_service_delete_contact_success(mock_delete, mock_get_id, mock_notify_deleted, mock_user):
    from vaultpass_backend.services.trusted_contact import TrustedContactService
    import asyncio

    contact_id = uuid.uuid4()
    mock_contact = MagicMock(spec=TrustedContact)
    mock_contact.id = contact_id
    mock_contact.owner_id = mock_user.id

    mock_get_id.return_value = mock_contact
    mock_db = AsyncMock()

    async def run_test():
        await TrustedContactService.delete_contact(mock_db, contact_id, mock_user.id)

    asyncio.run(run_test())
    mock_delete.assert_called_once_with(mock_db, mock_contact)
