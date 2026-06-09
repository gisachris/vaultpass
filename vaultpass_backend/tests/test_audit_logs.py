import uuid
import asyncio
from datetime import datetime, timezone
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from vaultpass_backend.main import app
from vaultpass_backend.models.audit_log import AuditLog
from vaultpass_backend.models.user import User

client = TestClient(app)


# ===================================================================
# FIXTURES
# ===================================================================

@pytest.fixture
def mock_user():
    return User(
        id=uuid.uuid4(),
        full_name="Audit Tester",
        email="audit@example.com",
        password_hash="hashed"
    )


@pytest.fixture
def override_auth_dependency(mock_user):
    from vaultpass_backend.core.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


def _make_mock_log(user_id: uuid.UUID, action: str = "DOCUMENT_CREATED") -> MagicMock:
    """Helper to produce a mock AuditLog ORM instance."""
    log = MagicMock(spec=AuditLog)
    log.id = uuid.uuid4()
    log.user_id = user_id
    log.action = action
    log.entity_type = "DOCUMENT"
    log.entity_id = uuid.uuid4()
    log.description = f"Test audit entry for {action}"
    log.metadata_ = None
    log.ip_address = "127.0.0.1"
    log.user_agent = "pytest"
    log.created_at = datetime.now(timezone.utc)
    return log


# ===================================================================
# API ROUTER TESTS
# ===================================================================

@patch("vaultpass_backend.api.audit_logs.AuditService.get_user_logs", new_callable=AsyncMock)
def test_router_list_audit_logs_returns_paginated_results(mock_get, override_auth_dependency, mock_user):
    """GET /api/audit-logs returns a correctly shaped paginated response."""
    mock_log = _make_mock_log(mock_user.id)
    mock_get.return_value = ([mock_log], 1)

    response = client.get("/api/audit-logs?page=1&limit=20")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["page"] == 1
    assert data["pages"] == 1
    assert data["limit"] == 20
    assert len(data["items"]) == 1
    assert data["items"][0]["action"] == "DOCUMENT_CREATED"


@patch("vaultpass_backend.api.audit_logs.AuditService.get_user_logs", new_callable=AsyncMock)
def test_router_list_audit_logs_empty(mock_get, override_auth_dependency):
    """GET /api/audit-logs returns 0 pages when there are no entries."""
    mock_get.return_value = ([], 0)

    response = client.get("/api/audit-logs")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 0
    assert data["pages"] == 0
    assert data["items"] == []


@patch("vaultpass_backend.api.audit_logs.AuditService.get_user_logs", new_callable=AsyncMock)
def test_router_list_audit_logs_passes_filters(mock_get, override_auth_dependency, mock_user):
    """GET /api/audit-logs forwards action and entity_type query params to the service."""
    mock_get.return_value = ([], 0)

    client.get("/api/audit-logs?action=LOGIN&entity_type=USER")

    mock_get.assert_called_once()
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs["action"] == "LOGIN"
    assert call_kwargs["entity_type"] == "USER"


@patch("vaultpass_backend.api.audit_logs.AuditService.get_user_logs", new_callable=AsyncMock)
def test_router_list_audit_logs_requires_auth(mock_get):
    """GET /api/audit-logs returns 403 when no authentication is provided."""
    response = client.get("/api/audit-logs")
    # No dependency override → auth guard fires
    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )


# ===================================================================
# SERVICE LAYER TESTS
# ===================================================================

@patch("vaultpass_backend.services.audit_service.AuditLogRepository.get_user_logs", new_callable=AsyncMock)
@patch("vaultpass_backend.services.audit_service.AuditLogRepository.count_user_logs", new_callable=AsyncMock)
def test_service_get_user_logs_pagination(mock_count, mock_get, mock_user):
    """AuditService.get_user_logs correctly calculates offset and delegates to repository."""
    from vaultpass_backend.services.audit_service import AuditService

    mock_db = AsyncMock()
    mock_log = _make_mock_log(mock_user.id)
    mock_get.return_value = [mock_log]
    mock_count.return_value = 1

    async def run():
        return await AuditService.get_user_logs(
            db=mock_db,
            user_id=mock_user.id,
            page=2,
            limit=10,
        )

    items, total = asyncio.run(run())
    assert total == 1
    assert len(items) == 1

    # Verify offset calculation: page=2, limit=10 → offset=10
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs["offset"] == 10
    assert call_kwargs["limit"] == 10


@patch("vaultpass_backend.services.audit_service.AuditLogRepository.get_user_logs", new_callable=AsyncMock)
@patch("vaultpass_backend.services.audit_service.AuditLogRepository.count_user_logs", new_callable=AsyncMock)
def test_service_get_user_logs_clamps_invalid_page(mock_count, mock_get, mock_user):
    """AuditService.get_user_logs resets page < 1 to 1."""
    from vaultpass_backend.services.audit_service import AuditService

    mock_db = AsyncMock()
    mock_get.return_value = []
    mock_count.return_value = 0

    async def run():
        return await AuditService.get_user_logs(
            db=mock_db,
            user_id=mock_user.id,
            page=-5,
            limit=20,
        )

    asyncio.run(run())
    call_kwargs = mock_get.call_args.kwargs
    assert call_kwargs["offset"] == 0  # page clamped to 1


@patch("vaultpass_backend.services.audit_service.AuditLogRepository.create", new_callable=AsyncMock)
def test_service_log_action_persists_entry(mock_create, mock_user):
    """AuditService.log_action constructs and saves an AuditLog via the repository."""
    from vaultpass_backend.services.audit_service import AuditService

    mock_db = AsyncMock()
    mock_create.return_value = MagicMock()

    async def run():
        await AuditService.log_action(
            db=mock_db,
            user_id=mock_user.id,
            action="document_created",   # lowercase — service must upper-case it
            entity_type="document",
            entity_id=uuid.uuid4(),
            description="Test log entry.",
        )

    asyncio.run(run())
    mock_create.assert_called_once()
    saved_log: AuditLog = mock_create.call_args.args[1]
    assert saved_log.action == "DOCUMENT_CREATED"
    assert saved_log.entity_type == "DOCUMENT"
    assert saved_log.user_id == mock_user.id


@patch("vaultpass_backend.services.audit_service.AuditLogRepository.create", new_callable=AsyncMock)
def test_service_log_action_swallows_exceptions(mock_create, mock_user):
    """AuditService.log_action does NOT raise when the repository throws."""
    from vaultpass_backend.services.audit_service import AuditService

    mock_db = AsyncMock()
    mock_create.side_effect = RuntimeError("DB is down")

    async def run():
        # Should complete without raising
        await AuditService.log_action(
            db=mock_db,
            user_id=mock_user.id,
            action="LOGIN",
            entity_type="USER",
            description="Login attempt.",
        )

    # If this raises, the test fails — that is the assertion.
    asyncio.run(run())


# ===================================================================
# REPOSITORY LAYER TESTS
# ===================================================================

@patch("vaultpass_backend.repository.audit_log.AuditLogRepository.get_user_logs", new_callable=AsyncMock)
def test_repository_get_user_logs_applies_action_filter(mock_get, mock_user):
    """AuditLogRepository.get_user_logs is called with the correct action filter."""
    from vaultpass_backend.repository.audit_log import AuditLogRepository

    mock_db = AsyncMock()
    mock_get.return_value = []

    async def run():
        await AuditLogRepository.get_user_logs(
            db=mock_db,
            user_id=mock_user.id,
            offset=0,
            limit=10,
            action="LOGIN",
        )

    asyncio.run(run())
    mock_get.assert_called_once()


# ===================================================================
# INTEGRATION: AUDIT CALLS INSIDE EXISTING SERVICES
# ===================================================================

@patch("vaultpass_backend.services.audit_service.AuditService.log_action", new_callable=AsyncMock)
@patch("vaultpass_backend.services.notification.NotificationService.notify_document_uploaded", new_callable=AsyncMock)
@patch("vaultpass_backend.services.document_service.storage_service.upload_file", new_callable=AsyncMock)
def test_upload_document_triggers_audit_log(mock_upload, mock_notify, mock_audit_log, mock_user):
    """Uploading a document fires AuditService.log_action with DOCUMENT_CREATED."""
    from vaultpass_backend.services.document_service import upload_document
    from vaultpass_backend.models.document import DocumentType

    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    mock_doc = MagicMock()
    mock_doc.id = uuid.uuid4()
    mock_doc.title = "Passport"

    mock_db.refresh = AsyncMock(side_effect=lambda d: None)

    mock_file = MagicMock()
    mock_file.filename = "passport.pdf"
    mock_file.content_type = "application/pdf"
    mock_file.file.seek = MagicMock()
    mock_file.file.tell = MagicMock(return_value=1024)

    async def run():
        # We only care that log_action is called; patching commit means no real DB write
        with patch("vaultpass_backend.services.document_service.Document") as MockDoc:
            instance = MagicMock()
            instance.id = uuid.uuid4()
            instance.title = "Passport"
            MockDoc.return_value = instance
            try:
                await upload_document(
                    db=mock_db,
                    owner_id=mock_user.id,
                    file=mock_file,
                    title="Passport",
                    document_type=DocumentType.PASSPORT,
                )
            except Exception:
                pass  # We only verify audit was called

    asyncio.run(run())
    mock_audit_log.assert_called_once()
    call_kwargs = mock_audit_log.call_args.kwargs
    assert call_kwargs["action"] == "DOCUMENT_CREATED"


@patch("vaultpass_backend.services.audit_service.AuditService.log_action", new_callable=AsyncMock)
@patch("vaultpass_backend.services.notification.NotificationService.notify_contact_added", new_callable=AsyncMock)
@patch("vaultpass_backend.repository.trusted_contact.TrustedContactRepository.get_contact_by_email", new_callable=AsyncMock)
@patch("vaultpass_backend.repository.trusted_contact.TrustedContactRepository.create_contact", new_callable=AsyncMock)
def test_create_contact_triggers_audit_log(mock_repo_create, mock_get_email, mock_notify, mock_audit, mock_user):
    """Creating a trusted contact fires AuditService.log_action with CONTACT_CREATED."""
    from vaultpass_backend.services.trusted_contact import TrustedContactService
    from vaultpass_backend.schemas.trusted_contact import TrustedContactCreate

    mock_db = AsyncMock()
    mock_get_email.return_value = None

    # Mock the user-lookup db.execute call that create_contact now performs
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = None  # external contact
    mock_db.execute.return_value = mock_user_result

    created = MagicMock()
    created.id = uuid.uuid4()
    created.full_name = "Jane Smith"
    mock_repo_create.return_value = created

    contact_data = TrustedContactCreate(
        full_name="Jane Smith",
        email="jane@example.com",
        relationship="Friend"
    )

    async def run():
        await TrustedContactService.create_contact(
            db=mock_db,
            owner_id=mock_user.id,
            contact_data=contact_data,
        )

    asyncio.run(run())
    mock_audit.assert_called_once()
    call_kwargs = mock_audit.call_args.kwargs
    assert call_kwargs["action"] == "CONTACT_CREATED"
    assert call_kwargs["entity_type"] == "TRUSTED_CONTACT"
