import uuid
from datetime import datetime, timezone, timedelta
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from vaultpass_backend.main import app
from vaultpass_backend.models.notification import Notification, NotificationType
from vaultpass_backend.models.user import User
from vaultpass_backend.models.document import Document
from vaultpass_backend.models.document_share import DocumentShare

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

@patch("vaultpass_backend.api.notifications.NotificationService.get_user_notifications", new_callable=AsyncMock)
def test_router_list_notifications(mock_get_notifications, override_auth_dependency, mock_user):
    notif_id = uuid.uuid4()
    mock_notif = MagicMock(spec=Notification)
    mock_notif.id = notif_id
    mock_notif.user_id = mock_user.id
    mock_notif.title = "Test Notification"
    mock_notif.message = "Hello world"
    mock_notif.type = NotificationType.INFO
    mock_notif.is_read = False
    mock_notif.related_document_id = None
    mock_notif.related_contact_id = None
    mock_notif.related_share_id = None
    mock_notif.created_at = datetime.now(timezone.utc)
    mock_notif.updated_at = None

    mock_get_notifications.return_value = ([mock_notif], 1)

    response = client.get("/api/notifications?page=1&limit=20")
    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()
    assert res_data["total"] == 1
    assert res_data["page"] == 1
    assert res_data["pages"] == 1
    assert len(res_data["items"]) == 1
    assert res_data["items"][0]["title"] == "Test Notification"


@patch("vaultpass_backend.api.notifications.NotificationService.get_unread_count", new_callable=AsyncMock)
def test_router_unread_count(mock_count, override_auth_dependency):
    mock_count.return_value = 5
    response = client.get("/api/notifications/unread-count")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["unread_count"] == 5


@patch("vaultpass_backend.api.notifications.NotificationService.get_notification", new_callable=AsyncMock)
def test_router_get_notification(mock_get, override_auth_dependency, mock_user):
    notif_id = uuid.uuid4()
    mock_notif = MagicMock(spec=Notification)
    mock_notif.id = notif_id
    mock_notif.user_id = mock_user.id
    mock_notif.title = "Details Test"
    mock_notif.message = "Msg"
    mock_notif.type = NotificationType.SUCCESS
    mock_notif.is_read = True
    mock_notif.related_document_id = None
    mock_notif.related_contact_id = None
    mock_notif.related_share_id = None
    mock_notif.created_at = datetime.now(timezone.utc)
    mock_notif.updated_at = None

    mock_get.return_value = mock_notif

    response = client.get(f"/api/notifications/{notif_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(notif_id)
    assert response.json()["title"] == "Details Test"


@patch("vaultpass_backend.api.notifications.NotificationService.mark_read", new_callable=AsyncMock)
def test_router_mark_read(mock_mark, override_auth_dependency, mock_user):
    notif_id = uuid.uuid4()
    mock_notif = MagicMock(spec=Notification)
    mock_notif.id = notif_id
    mock_notif.user_id = mock_user.id
    mock_notif.title = "Read Notification"
    mock_notif.message = "Msg"
    mock_notif.type = NotificationType.INFO
    mock_notif.is_read = True
    mock_notif.related_document_id = None
    mock_notif.related_contact_id = None
    mock_notif.related_share_id = None
    mock_notif.created_at = datetime.now(timezone.utc)
    mock_notif.updated_at = None

    mock_mark.return_value = mock_notif

    response = client.patch(f"/api/notifications/{notif_id}/read")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_read"] is True


@patch("vaultpass_backend.api.notifications.NotificationService.mark_unread", new_callable=AsyncMock)
def test_router_mark_unread(mock_mark, override_auth_dependency, mock_user):
    notif_id = uuid.uuid4()
    mock_notif = MagicMock(spec=Notification)
    mock_notif.id = notif_id
    mock_notif.user_id = mock_user.id
    mock_notif.title = "Unread Notification"
    mock_notif.message = "Msg"
    mock_notif.type = NotificationType.INFO
    mock_notif.is_read = False
    mock_notif.related_document_id = None
    mock_notif.related_contact_id = None
    mock_notif.related_share_id = None
    mock_notif.created_at = datetime.now(timezone.utc)
    mock_notif.updated_at = None

    mock_mark.return_value = mock_notif

    response = client.patch(f"/api/notifications/{notif_id}/unread")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_read"] is False


@patch("vaultpass_backend.api.notifications.NotificationService.mark_all_read", new_callable=AsyncMock)
def test_router_mark_all_read(mock_mark_all, override_auth_dependency):
    mock_mark_all.return_value = None
    response = client.patch("/api/notifications/read-all")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "All notifications marked as read"


@patch("vaultpass_backend.api.notifications.NotificationService.delete_notification", new_callable=AsyncMock)
def test_router_delete_notification(mock_delete, override_auth_dependency):
    notif_id = uuid.uuid4()
    mock_delete.return_value = None
    response = client.delete(f"/api/notifications/{notif_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Notification deleted successfully"


@patch("vaultpass_backend.api.notifications.NotificationService.delete_all_notifications", new_callable=AsyncMock)
def test_router_delete_all_notifications(mock_delete_all, override_auth_dependency):
    mock_delete_all.return_value = None
    response = client.delete("/api/notifications")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "All notifications deleted successfully"


# ================= SERVICE LAYER TESTS =================

@patch("vaultpass_backend.services.notification.NotificationRepository.create_notification", new_callable=AsyncMock)
def test_service_create_notification(mock_repo_create, mock_user):
    from vaultpass_backend.services.notification import NotificationService
    import asyncio

    mock_db = AsyncMock()
    mock_notif = MagicMock(spec=Notification)
    mock_notif.user_id = mock_user.id
    mock_notif.title = "Service Create Title"
    mock_notif.message = "Hello Service"
    mock_notif.type = NotificationType.SUCCESS

    mock_repo_create.return_value = mock_notif

    async def run_test():
        return await NotificationService.create_notification(
            db=mock_db,
            user_id=mock_user.id,
            title="Service Create Title",
            message="Hello Service",
            type=NotificationType.SUCCESS
        )

    res = asyncio.run(run_test())
    assert res.title == "Service Create Title"
    mock_repo_create.assert_called_once()


@patch("vaultpass_backend.services.notification.NotificationRepository.get_notification_by_id", new_callable=AsyncMock)
def test_service_get_notification_not_found(mock_repo_get, mock_user):
    from vaultpass_backend.services.notification import NotificationService
    from fastapi import HTTPException
    import asyncio

    mock_repo_get.return_value = None
    mock_db = AsyncMock()
    notif_id = uuid.uuid4()

    async def run_test():
        await NotificationService.get_notification(mock_db, notif_id, mock_user.id)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@patch("vaultpass_backend.services.notification.NotificationRepository.get_notification_by_id", new_callable=AsyncMock)
def test_service_get_notification_forbidden(mock_repo_get, mock_user):
    from vaultpass_backend.services.notification import NotificationService
    from fastapi import HTTPException
    import asyncio

    mock_notif = MagicMock(spec=Notification)
    mock_notif.user_id = uuid.uuid4() # Different user ID

    mock_repo_get.return_value = mock_notif
    mock_db = AsyncMock()
    notif_id = uuid.uuid4()

    async def run_test():
        await NotificationService.get_notification(mock_db, notif_id, mock_user.id)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(run_test())
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


# ================= SCHEDULER & EVENT HOOK TESTS =================

@patch("vaultpass_backend.repository.settings_repository.SettingsRepository.get_by_user_id", new_callable=AsyncMock)
@patch("vaultpass_backend.services.notification.NotificationService.create_notification", new_callable=AsyncMock)
def test_scheduler_checks_expiring_resources(mock_create_notif, mock_get_settings):
    from vaultpass_backend.services.notification_scheduler import NotificationScheduler
    import asyncio

    # Return a mock settings object with notifications enabled and default 30-day reminder
    mock_settings = MagicMock()
    mock_settings.document_expiry_notifications = True
    mock_settings.document_reminder_days = 30
    mock_get_settings.return_value = mock_settings

    mock_db = AsyncMock()
    
    # 1. Setup mock documents
    # Doc A: Expiring in 14 days (milestone)
    # Doc B: Expired
    # Doc C: Expiring in 5 days (no milestone)
    doc_a = MagicMock(spec=Document)
    doc_a.id = uuid.uuid4()
    doc_a.owner_id = uuid.uuid4()
    doc_a.title = "Doc A"
    doc_a.expiry_date = datetime.now(timezone.utc) + timedelta(days=14)

    doc_b = MagicMock(spec=Document)
    doc_b.id = uuid.uuid4()
    doc_b.owner_id = uuid.uuid4()
    doc_b.title = "Doc B"
    doc_b.expiry_date = datetime.now(timezone.utc) - timedelta(days=1)

    doc_c = MagicMock(spec=Document)
    doc_c.id = uuid.uuid4()
    doc_c.owner_id = uuid.uuid4()
    doc_c.title = "Doc C"
    doc_c.expiry_date = datetime.now(timezone.utc) + timedelta(days=5)

    mock_doc_result = MagicMock()
    mock_doc_result.scalars.return_value.all.return_value = [doc_a, doc_b, doc_c]

    # 2. Setup mock shares
    # Share A: Active and expired
    # Share B: Active and not expired
    share_a = MagicMock(spec=DocumentShare)
    share_a.id = uuid.uuid4()
    share_a.owner_id = uuid.uuid4()
    share_a.document_id = uuid.uuid4()
    share_a.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    share_a.is_active = True

    share_b = MagicMock(spec=DocumentShare)
    share_b.id = uuid.uuid4()
    share_b.owner_id = uuid.uuid4()
    share_b.document_id = uuid.uuid4()
    share_b.expires_at = datetime.now(timezone.utc) + timedelta(days=10)
    share_b.is_active = True

    mock_share_result = MagicMock()
    mock_share_result.scalars.return_value.all.return_value = [share_a, share_b]

    # Setup DB execution
    # First query fetches documents. Second query searches existing notifications (mocked as None for simplicity).
    # Then fetches shares. Then searches existing notifications.
    mock_db.execute.side_effect = [
        mock_doc_result,
        MagicMock(scalar_one_or_none=lambda: None), # Doc A check reminder
        MagicMock(scalar_one_or_none=lambda: None), # Doc B check expired
        mock_share_result,
        MagicMock(scalar_one_or_none=lambda: None), # Share A check expired
        MagicMock(scalar=lambda: "Doc A Share Title") # Share A doc title fetch query
    ]

    async def run_test():
        await NotificationScheduler.check_expiring_resources(mock_db)

    asyncio.run(run_test())

    # We expect 3 notification generation helper calls:
    # 1. notify_document_expiring for Doc A (14 days reminder)
    # 2. notify_document_expired for Doc B (Expired error)
    # 3. notify_share_expired for Share A (Expired warning)
    # Note that Doc C should not trigger anything because 5 days is not a milestone.
    # Share B should not trigger anything because it is not expired.
    assert mock_create_notif.call_count == 3
