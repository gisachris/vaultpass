import uuid
from datetime import datetime, timezone
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from vaultpass_backend.main import app
from vaultpass_backend.models.family_relationship import FamilyRelationship, RelationshipType, RelationshipStatus
from vaultpass_backend.models.user import User
from vaultpass_backend.models.document import Document, DocumentType

client = TestClient(app)

@pytest.fixture
def mock_user_guardian():
    return User(
        id=uuid.uuid4(),
        full_name="Guardian Joe",
        email="guardian@example.com",
        password_hash="hashed_password",
        is_active=True
    )

@pytest.fixture
def mock_user_dependent():
    return User(
        id=uuid.uuid4(),
        full_name="Dependent Kid",
        email="dependent@example.com",
        password_hash="hashed_password",
        is_active=True
    )

@pytest.fixture
def override_guardian_auth(mock_user_guardian):
    from vaultpass_backend.core.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: mock_user_guardian
    yield
    app.dependency_overrides.pop(get_current_user, None)

@pytest.fixture
def override_dependent_auth(mock_user_dependent):
    from vaultpass_backend.core.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: mock_user_dependent
    yield
    app.dependency_overrides.pop(get_current_user, None)

# ================= ROUTER / API TESTS =================

@patch("vaultpass_backend.api.family.FamilyService.create_invitation", new_callable=AsyncMock)
def test_router_create_invitation_success(mock_create_inv, override_guardian_auth, mock_user_guardian, mock_user_dependent):
    relation_id = uuid.uuid4()
    mock_relation = MagicMock(spec=FamilyRelationship)
    mock_relation.id = relation_id
    mock_relation.guardian_id = mock_user_guardian.id
    mock_relation.dependent_id = mock_user_dependent.id
    mock_relation.relationship = RelationshipType.PARENT
    mock_relation.status = RelationshipStatus.PENDING
    mock_relation.created_at = datetime.now(timezone.utc)
    mock_relation.accepted_at = None
    mock_relation.invited_by = mock_user_guardian.id
    mock_relation.notes = "Parental guardianship"
    mock_relation.guardian = mock_user_guardian
    mock_relation.dependent = mock_user_dependent

    mock_create_inv.return_value = mock_relation

    payload = {
        "email": "dependent@example.com",
        "relationship": "PARENT",
        "notes": "Parental guardianship"
    }

    response = client.post("/api/family/invitations", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    res_data = response.json()
    assert res_data["id"] == str(relation_id)
    assert res_data["relationship"] == "PARENT"
    assert res_data["status"] == "PENDING"

@patch("vaultpass_backend.api.family.FamilyService.get_sent_invitations", new_callable=AsyncMock)
def test_router_list_sent_invitations(mock_get_sent, override_guardian_auth, mock_user_guardian, mock_user_dependent):
    mock_relation = MagicMock(spec=FamilyRelationship)
    mock_relation.id = uuid.uuid4()
    mock_relation.guardian_id = mock_user_guardian.id
    mock_relation.dependent_id = mock_user_dependent.id
    mock_relation.relationship = RelationshipType.PARENT
    mock_relation.status = RelationshipStatus.PENDING
    mock_relation.created_at = datetime.now(timezone.utc)
    mock_relation.accepted_at = None
    mock_relation.invited_by = mock_user_guardian.id
    mock_relation.notes = None
    mock_relation.guardian = mock_user_guardian
    mock_relation.dependent = mock_user_dependent

    mock_get_sent.return_value = [mock_relation]

    response = client.get("/api/family/invitations/sent")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "PENDING"

@patch("vaultpass_backend.api.family.FamilyService.get_received_invitations", new_callable=AsyncMock)
def test_router_list_received_invitations(mock_get_recv, override_dependent_auth, mock_user_guardian, mock_user_dependent):
    mock_relation = MagicMock(spec=FamilyRelationship)
    mock_relation.id = uuid.uuid4()
    mock_relation.guardian_id = mock_user_guardian.id
    mock_relation.dependent_id = mock_user_dependent.id
    mock_relation.relationship = RelationshipType.CHILD
    mock_relation.status = RelationshipStatus.PENDING
    mock_relation.created_at = datetime.now(timezone.utc)
    mock_relation.accepted_at = None
    mock_relation.invited_by = mock_user_guardian.id
    mock_relation.notes = None
    mock_relation.guardian = mock_user_guardian
    mock_relation.dependent = mock_user_dependent

    mock_get_recv.return_value = [mock_relation]

    response = client.get("/api/family/invitations/received")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

@patch("vaultpass_backend.api.family.FamilyService.accept_invitation", new_callable=AsyncMock)
def test_router_accept_invitation(mock_accept, override_dependent_auth, mock_user_guardian, mock_user_dependent):
    relation_id = uuid.uuid4()
    mock_relation = MagicMock(spec=FamilyRelationship)
    mock_relation.id = relation_id
    mock_relation.guardian_id = mock_user_guardian.id
    mock_relation.dependent_id = mock_user_dependent.id
    mock_relation.relationship = RelationshipType.CHILD
    mock_relation.status = RelationshipStatus.ACCEPTED
    mock_relation.created_at = datetime.now(timezone.utc)
    mock_relation.accepted_at = datetime.now(timezone.utc)
    mock_relation.invited_by = mock_user_guardian.id
    mock_relation.notes = None
    mock_relation.guardian = mock_user_guardian
    mock_relation.dependent = mock_user_dependent

    mock_accept.return_value = mock_relation

    response = client.post(f"/api/family/invitations/{relation_id}/accept")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "ACCEPTED"

@patch("vaultpass_backend.api.family.FamilyService.decline_invitation", new_callable=AsyncMock)
def test_router_decline_invitation(mock_decline, override_dependent_auth, mock_user_guardian, mock_user_dependent):
    relation_id = uuid.uuid4()
    mock_relation = MagicMock(spec=FamilyRelationship)
    mock_relation.id = relation_id
    mock_relation.guardian_id = mock_user_guardian.id
    mock_relation.dependent_id = mock_user_dependent.id
    mock_relation.relationship = RelationshipType.CHILD
    mock_relation.status = RelationshipStatus.DECLINED
    mock_relation.created_at = datetime.now(timezone.utc)
    mock_relation.accepted_at = None
    mock_relation.invited_by = mock_user_guardian.id
    mock_relation.notes = None
    mock_relation.guardian = mock_user_guardian
    mock_relation.dependent = mock_user_dependent

    mock_decline.return_value = mock_relation

    response = client.post(f"/api/family/invitations/{relation_id}/decline")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "DECLINED"

@patch("vaultpass_backend.api.family.FamilyService.remove_relationship", new_callable=AsyncMock)
def test_router_remove_relationship(mock_remove, override_guardian_auth):
    relation_id = uuid.uuid4()
    mock_remove.return_value = None

    response = client.delete(f"/api/family/{relation_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Family relationship removed successfully"

@patch("vaultpass_backend.api.family.FamilyService.get_family_members", new_callable=AsyncMock)
def test_router_list_family_members(mock_get_members, override_guardian_auth, mock_user_guardian, mock_user_dependent):
    mock_relation = MagicMock(spec=FamilyRelationship)
    mock_relation.id = uuid.uuid4()
    mock_relation.guardian_id = mock_user_guardian.id
    mock_relation.dependent_id = mock_user_dependent.id
    mock_relation.relationship = RelationshipType.PARENT
    mock_relation.status = RelationshipStatus.ACCEPTED
    mock_relation.created_at = datetime.now(timezone.utc)
    mock_relation.guardian = mock_user_guardian
    mock_relation.dependent = mock_user_dependent

    mock_get_members.return_value = [mock_relation]

    response = client.get("/api/family")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

@patch("vaultpass_backend.api.family.FamilyService.get_guardian_documents", new_callable=AsyncMock)
def test_router_family_documents(mock_get_docs, override_guardian_auth):
    mock_get_docs.return_value = [
        {
            "dependent_id": uuid.uuid4(),
            "dependent_name": "Kid Doe",
            "relationship": "PARENT",
            "documents": [
                {
                    "id": uuid.uuid4(),
                    "owner_id": uuid.uuid4(),
                    "title": "Birth Certificate",
                    "document_type": "BIRTH_CERTIFICATE",
                    "file_name": "birth.pdf",
                    "file_path": "path/birth.pdf",
                    "file_size": 1024,
                    "mime_type": "application/pdf",
                    "uploaded_at": datetime.now(timezone.utc).isoformat(),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ]
        }
    ]

    response = client.get("/api/family/documents?page=1&limit=10")
    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()
    assert len(res_data) == 1
    assert res_data[0]["dependent_name"] == "Kid Doe"
    assert len(res_data[0]["documents"]) == 1

@patch("vaultpass_backend.api.family.FamilyService.get_family_summary", new_callable=AsyncMock)
def test_router_family_summary(mock_summary, override_guardian_auth):
    mock_summary.return_value = {
        "family_members": 2,
        "guardian_count": 1,
        "dependent_count": 1,
        "accessible_documents": 5,
        "pending_invitations": 0
    }

    response = client.get("/api/family/summary")
    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()
    assert res_data["accessible_documents"] == 5

# ================= SERVICE LAYER TESTS =================

@patch("vaultpass_backend.services.family.NotificationService.create_notification", new_callable=AsyncMock)
@patch("vaultpass_backend.services.family.AuditService.log_action", new_callable=AsyncMock)
@patch("vaultpass_backend.services.family.FamilyRepository.create_relationship", new_callable=AsyncMock)
@patch("vaultpass_backend.services.family.FamilyRepository.get_active_or_pending_between_users", new_callable=AsyncMock)
def test_service_create_invitation_success(mock_check_exist, mock_create, mock_audit, mock_notify, mock_user_guardian, mock_user_dependent):
    from vaultpass_backend.services.family import FamilyService
    from vaultpass_backend.schemas.family import FamilyInvitationCreate
    import asyncio

    mock_check_exist.return_value = None

    mock_db = AsyncMock()
    # Mock invitee email lookup
    mock_recipient_result = MagicMock()
    mock_recipient_result.scalar_one_or_none.return_value = mock_user_dependent
    # Mock sender lookup
    mock_sender_result = MagicMock()
    mock_sender_result.scalar_one.return_value = mock_user_guardian
    mock_db.execute.side_effect = [mock_recipient_result, mock_sender_result]

    created_relation = FamilyRelationship(
        id=uuid.uuid4(),
        guardian_id=mock_user_guardian.id,
        dependent_id=mock_user_dependent.id,
        relationship=RelationshipType.PARENT,
        status=RelationshipStatus.PENDING,
        invited_by=mock_user_guardian.id
    )
    mock_create.return_value = created_relation

    inv_data = FamilyInvitationCreate(
        email="dependent@example.com",
        relationship=RelationshipType.PARENT,
        notes="Parent guardianship setup"
    )

    async def run_test():
        return await FamilyService.create_invitation(mock_db, mock_user_guardian.id, inv_data)

    res = asyncio.run(run_test())
    assert res.guardian_id == mock_user_guardian.id
    assert res.dependent_id == mock_user_dependent.id
    mock_create.assert_called_once()
    mock_notify.assert_called_once()
    mock_audit.assert_called_once()

@patch("vaultpass_backend.services.family.FamilyRepository.get_active_or_pending_between_users", new_callable=AsyncMock)
def test_service_create_invitation_duplicate(mock_check_exist, mock_user_guardian, mock_user_dependent):
    from vaultpass_backend.services.family import FamilyService
    from vaultpass_backend.schemas.family import FamilyInvitationCreate
    from fastapi import HTTPException
    import asyncio

    existing_relation = MagicMock(spec=FamilyRelationship)
    existing_relation.status = RelationshipStatus.ACCEPTED
    mock_check_exist.return_value = existing_relation

    mock_db = AsyncMock()
    mock_recipient_result = MagicMock()
    mock_recipient_result.scalar_one_or_none.return_value = mock_user_dependent
    mock_db.execute.return_value = mock_recipient_result

    inv_data = FamilyInvitationCreate(
        email="dependent@example.com",
        relationship=RelationshipType.PARENT
    )

    async def run_test():
        await FamilyService.create_invitation(mock_db, mock_user_guardian.id, inv_data)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())
        
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "active relationship already exists" in exc_info.value.detail

@patch("vaultpass_backend.services.family.FamilyRepository.get_active_or_pending_between_users", new_callable=AsyncMock)
def test_service_create_invitation_self(mock_check_exist, mock_user_guardian):
    from vaultpass_backend.services.family import FamilyService
    from vaultpass_backend.schemas.family import FamilyInvitationCreate
    from fastapi import HTTPException
    import asyncio

    mock_db = AsyncMock()
    mock_recipient_result = MagicMock()
    mock_recipient_result.scalar_one_or_none.return_value = mock_user_guardian
    mock_db.execute.return_value = mock_recipient_result

    inv_data = FamilyInvitationCreate(
        email="guardian@example.com",
        relationship=RelationshipType.PARENT
    )

    async def run_test():
        await FamilyService.create_invitation(mock_db, mock_user_guardian.id, inv_data)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())
        
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot invite yourself" in exc_info.value.detail

# ================= ACCESS RESOLUTION TESTS =================

@patch("vaultpass_backend.repository.family.FamilyRepository.check_is_guardian", new_callable=AsyncMock)
def test_document_access_service_guardian_success(mock_is_guardian, mock_user_guardian, mock_user_dependent):
    from vaultpass_backend.services.document_access_service import DocumentAccessService
    import asyncio

    mock_is_guardian.return_value = True

    doc_id = uuid.uuid4()
    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = mock_user_dependent.id

    mock_db = AsyncMock()
    mock_doc_result = MagicMock()
    mock_doc_result.scalar_one_or_none.return_value = mock_doc
    mock_db.execute.return_value = mock_doc_result

    async def run_test():
        return await DocumentAccessService.resolve_document_access(mock_db, doc_id, mock_user_guardian.id)

    doc, share = asyncio.run(run_test())
    assert doc == mock_doc
    assert share is None
    mock_is_guardian.assert_called_once_with(mock_db, guardian_id=mock_user_guardian.id, dependent_id=mock_user_dependent.id)

def test_guardian_cannot_modify_document(override_guardian_auth, mock_user_guardian, mock_user_dependent):
    # Testing that write operations on document endpoints reject guardians
    doc_id = uuid.uuid4()
    payload = {
        "title": "Malicious Renaming Attempt",
        "document_type": "PASSPORT"
    }

    # Simulate get_document_by_id checks inside document router
    # We patch the DB call to return a document owned by dependent
    mock_doc = MagicMock(spec=Document)
    mock_doc.id = doc_id
    mock_doc.owner_id = mock_user_dependent.id

    with patch("vaultpass_backend.services.document_service.select") as mock_select:
        mock_db = AsyncMock()
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = mock_doc
        mock_db.execute.return_value = mock_res
        
        # Override DB dependency in FastAPI app
        from vaultpass_backend.core.dependencies import get_db
        app.dependency_overrides[get_db] = lambda: mock_db
        
        response = client.put(f"/api/documents/{doc_id}", json=payload)
        
        # Should return 403 because update check passes allow_guardian=False to get_document_by_id
        assert response.status_code == status.HTTP_403_FORBIDDEN
        app.dependency_overrides.pop(get_db, None)
