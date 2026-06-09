import re
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

class ProfileSettingsResponse(BaseModel):
    full_name: str
    email: EmailStr
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class ProfileSettingsUpdate(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=255, description="Full name (minimum 3 characters)")

class SecuritySettingsResponse(BaseModel):
    two_factor_enabled: bool
    auto_logout_enabled: bool
    session_timeout_minutes: int

    model_config = {
        "from_attributes": True
    }

class SecuritySettingsUpdate(BaseModel):
    two_factor_enabled: bool
    auto_logout_enabled: bool
    session_timeout_minutes: int = Field(..., ge=5, le=1440, description="Session timeout in minutes (5 to 1440)")

class NotificationSettingsResponse(BaseModel):
    email_notifications: bool
    push_notifications: bool
    document_expiry_notifications: bool
    shared_access_notifications: bool
    trusted_contact_notifications: bool
    security_alert_notifications: bool
    weekly_summary_notifications: bool

    model_config = {
        "from_attributes": True
    }

class NotificationSettingsUpdate(BaseModel):
    email_notifications: bool
    push_notifications: bool
    document_expiry_notifications: bool
    shared_access_notifications: bool
    trusted_contact_notifications: bool
    security_alert_notifications: bool
    weekly_summary_notifications: bool

class PrivacySettingsResponse(BaseModel):
    allow_profile_visibility: bool
    allow_contact_visibility: bool

    model_config = {
        "from_attributes": True
    }

class PrivacySettingsUpdate(BaseModel):
    allow_profile_visibility: bool
    allow_contact_visibility: bool

class ReminderSettingsResponse(BaseModel):
    document_reminder_days: int

    model_config = {
        "from_attributes": True
    }

class ReminderSettingsUpdate(BaseModel):
    document_reminder_days: int = Field(..., ge=1, le=365, description="Document reminder days (1 to 365)")

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> 'ChangePasswordRequest':
        if self.new_password == self.current_password:
            raise ValueError("New password cannot equal old password")
        if self.new_password != self.confirm_password:
            raise ValueError("Confirm password must match new password")
        return self

class DeactivateRequest(BaseModel):
    password: str

class AccountInfoResponse(BaseModel):
    account_created: datetime
    last_login: Optional[datetime] = None
    documents_count: int
    trusted_contacts_count: int
    active_shares_count: int

class AccountSettingsExportResponse(BaseModel):
    profile: dict
    security: dict
    notifications: dict
    privacy: dict
    reminders: dict
