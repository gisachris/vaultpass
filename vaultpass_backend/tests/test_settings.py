import uuid
from datetime import datetime, timezone
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from vaultpass_backend.main import app
from vaultpass_backend.models.user import User
from vaultpass_backend.models.settings import UserSettings

client = TestClient(app)

@pytest.fixture
def mock_user():
    user = User(
        id=uuid.uuid4(),
        full_name="John Doe",
        email="john@example.com",
        password_hash="hashed_password",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        last_login=datetime.now(timezone.utc),
    )
    return user

@pytest.fixture
def override_auth_dependency(mock_user):
    from vaultpass_backend.core.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.pop(get_current_user, None)

# ================= PROFILE SETTINGS =================

@patch("vaultpass_backend.api.settings_router.SettingsService.get_profile", new_callable=AsyncMock)
def test_get_profile(mock_get_profile, override_auth_dependency, mock_user):
    from vaultpass_backend.schemas.settings import ProfileSettingsResponse
    mock_get_profile.return_value = ProfileSettingsResponse(
        full_name=mock_user.full_name,
        email=mock_user.email,
        created_at=mock_user.created_at,
        last_login=mock_user.last_login
    )

    response = client.get("/api/settings/profile")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == "John Doe"
    assert response.json()["email"] == "john@example.com"

@patch("vaultpass_backend.api.settings_router.SettingsService.update_profile", new_callable=AsyncMock)
def test_update_profile(mock_update_profile, override_auth_dependency, mock_user):
    from vaultpass_backend.schemas.settings import ProfileSettingsResponse
    mock_update_profile.return_value = ProfileSettingsResponse(
        full_name="Johnny Doe",
        email=mock_user.email,
        created_at=mock_user.created_at,
        last_login=mock_user.last_login
    )

    response = client.put("/api/settings/profile", json={"full_name": "Johnny Doe"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == "Johnny Doe"

def test_update_profile_validation_failure(override_auth_dependency):
    response = client.put("/api/settings/profile", json={"full_name": "Jo"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# ================= SECURITY SETTINGS =================

@patch("vaultpass_backend.api.settings_router.SettingsService.get_security", new_callable=AsyncMock)
def test_get_security(mock_get_security, override_auth_dependency):
    from vaultpass_backend.schemas.settings import SecuritySettingsResponse
    mock_get_security.return_value = SecuritySettingsResponse(
        two_factor_enabled=False,
        auto_logout_enabled=True,
        session_timeout_minutes=30
    )

    response = client.get("/api/settings/security")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["two_factor_enabled"] is False
    assert response.json()["session_timeout_minutes"] == 30

@patch("vaultpass_backend.api.settings_router.SettingsService.update_security", new_callable=AsyncMock)
def test_update_security(mock_update_security, override_auth_dependency):
    from vaultpass_backend.schemas.settings import SecuritySettingsResponse
    mock_update_security.return_value = SecuritySettingsResponse(
        two_factor_enabled=True,
        auto_logout_enabled=True,
        session_timeout_minutes=15
    )

    response = client.put("/api/settings/security", json={
        "two_factor_enabled": True,
        "auto_logout_enabled": True,
        "session_timeout_minutes": 15
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["two_factor_enabled"] is True
    assert response.json()["session_timeout_minutes"] == 15

def test_update_security_validation_failure(override_auth_dependency):
    response = client.put("/api/settings/security", json={
        "two_factor_enabled": True,
        "auto_logout_enabled": True,
        "session_timeout_minutes": 4
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# ================= NOTIFICATION SETTINGS =================

@patch("vaultpass_backend.api.settings_router.SettingsService.get_notifications", new_callable=AsyncMock)
def test_get_notifications(mock_get_notifications, override_auth_dependency):
    from vaultpass_backend.schemas.settings import NotificationSettingsResponse
    mock_get_notifications.return_value = NotificationSettingsResponse(
        email_notifications=True,
        push_notifications=True,
        document_expiry_notifications=True,
        shared_access_notifications=True,
        trusted_contact_notifications=True,
        security_alert_notifications=True,
        weekly_summary_notifications=False
    )

    response = client.get("/api/settings/notifications")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email_notifications"] is True
    assert response.json()["weekly_summary_notifications"] is False

@patch("vaultpass_backend.api.settings_router.SettingsService.update_notifications", new_callable=AsyncMock)
def test_update_notifications(mock_update_notifications, override_auth_dependency):
    from vaultpass_backend.schemas.settings import NotificationSettingsResponse
    mock_update_notifications.return_value = NotificationSettingsResponse(
        email_notifications=True,
        push_notifications=False,
        document_expiry_notifications=True,
        shared_access_notifications=True,
        trusted_contact_notifications=False,
        security_alert_notifications=True,
        weekly_summary_notifications=True
    )

    response = client.put("/api/settings/notifications", json={
        "email_notifications": True,
        "push_notifications": False,
        "document_expiry_notifications": True,
        "shared_access_notifications": True,
        "trusted_contact_notifications": False,
        "security_alert_notifications": True,
        "weekly_summary_notifications": True
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["push_notifications"] is False
    assert response.json()["weekly_summary_notifications"] is True

# ================= PRIVACY SETTINGS =================

@patch("vaultpass_backend.api.settings_router.SettingsService.get_privacy", new_callable=AsyncMock)
def test_get_privacy(mock_get_privacy, override_auth_dependency):
    from vaultpass_backend.schemas.settings import PrivacySettingsResponse
    mock_get_privacy.return_value = PrivacySettingsResponse(
        allow_profile_visibility=False,
        allow_contact_visibility=False
    )

    response = client.get("/api/settings/privacy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["allow_profile_visibility"] is False

@patch("vaultpass_backend.api.settings_router.SettingsService.update_privacy", new_callable=AsyncMock)
def test_update_privacy(mock_update_privacy, override_auth_dependency):
    from vaultpass_backend.schemas.settings import PrivacySettingsResponse
    mock_update_privacy.return_value = PrivacySettingsResponse(
        allow_profile_visibility=True,
        allow_contact_visibility=False
    )

    response = client.put("/api/settings/privacy", json={
        "allow_profile_visibility": True,
        "allow_contact_visibility": False
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["allow_profile_visibility"] is True

# ================= REMINDER SETTINGS =================

@patch("vaultpass_backend.api.settings_router.SettingsService.get_reminders", new_callable=AsyncMock)
def test_get_reminders(mock_get_reminders, override_auth_dependency):
    from vaultpass_backend.schemas.settings import ReminderSettingsResponse
    mock_get_reminders.return_value = ReminderSettingsResponse(
        document_reminder_days=30
    )

    response = client.get("/api/settings/reminders")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["document_reminder_days"] == 30

@patch("vaultpass_backend.api.settings_router.SettingsService.update_reminders", new_callable=AsyncMock)
def test_update_reminders(mock_update_reminders, override_auth_dependency):
    from vaultpass_backend.schemas.settings import ReminderSettingsResponse
    mock_update_reminders.return_value = ReminderSettingsResponse(
        document_reminder_days=60
    )

    response = client.put("/api/settings/reminders", json={
        "document_reminder_days": 60
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["document_reminder_days"] == 60

def test_update_reminders_validation_failure(override_auth_dependency):
    response = client.put("/api/settings/reminders", json={
        "document_reminder_days": 0
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# ================= CHANGE PASSWORD =================

@patch("vaultpass_backend.api.settings_router.SettingsService.change_password", new_callable=AsyncMock)
def test_change_password(mock_change_password, override_auth_dependency):
    response = client.post("/api/settings/change-password", json={
        "current_password": "OldPassword123",
        "new_password": "NewPassword123",
        "confirm_password": "NewPassword123"
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Your account password was changed"
    mock_change_password.assert_called_once()

def test_change_password_validation_failure(override_auth_dependency):
    response = client.post("/api/settings/change-password", json={
        "current_password": "OldPassword123",
        "new_password": "short",
        "confirm_password": "short"
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# ================= ACCOUNT INFO & EXPORT =================

@patch("vaultpass_backend.api.settings_router.SettingsService.get_account_info", new_callable=AsyncMock)
def test_get_account_info(mock_get_account_info, override_auth_dependency, mock_user):
    from vaultpass_backend.schemas.settings import AccountInfoResponse
    mock_get_account_info.return_value = AccountInfoResponse(
        account_created=mock_user.created_at,
        last_login=mock_user.last_login,
        documents_count=5,
        trusted_contacts_count=2,
        active_shares_count=3
    )

    response = client.get("/api/settings/account")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["documents_count"] == 5
    assert response.json()["trusted_contacts_count"] == 2
    assert response.json()["active_shares_count"] == 3

@patch("vaultpass_backend.api.settings_router.SettingsService.export_settings", new_callable=AsyncMock)
def test_export_settings(mock_export_settings, override_auth_dependency):
    mock_export_settings.return_value = {
        "profile": {"full_name": "John Doe", "email": "john@example.com"},
        "security": {"two_factor_enabled": False, "auto_logout_enabled": True, "session_timeout_minutes": 30},
        "notifications": {"email_notifications": True},
        "privacy": {"allow_profile_visibility": False},
        "reminders": {"document_reminder_days": 30}
    }

    response = client.get("/api/settings/export")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["profile"]["full_name"] == "John Doe"
    assert data["security"]["session_timeout_minutes"] == 30

# ================= DEACTIVATION =================

@patch("vaultpass_backend.api.settings_router.SettingsService.deactivate_account", new_callable=AsyncMock)
def test_deactivate_account(mock_deactivate_account, override_auth_dependency):
    response = client.post("/api/settings/deactivate", json={"password": "MyPassword123"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Account deactivated successfully"
    mock_deactivate_account.assert_called_once()
