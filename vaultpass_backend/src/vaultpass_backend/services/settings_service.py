import uuid
from typing import Any, Dict
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.models.user import User
from vaultpass_backend.models.settings import UserSettings
from vaultpass_backend.models.document import Document
from vaultpass_backend.models.trusted_contact import TrustedContact
from vaultpass_backend.models.document_share import DocumentShare
from vaultpass_backend.repository.settings_repository import SettingsRepository
from vaultpass_backend.schemas.settings import (
    ProfileSettingsResponse,
    ProfileSettingsUpdate,
    SecuritySettingsResponse,
    SecuritySettingsUpdate,
    NotificationSettingsResponse,
    NotificationSettingsUpdate,
    PrivacySettingsResponse,
    PrivacySettingsUpdate,
    ReminderSettingsResponse,
    ReminderSettingsUpdate,
    ChangePasswordRequest,
    DeactivateRequest,
    AccountInfoResponse,
)
from vaultpass_backend.core.security import verify_password, get_password_hash
from vaultpass_backend.services.audit_service import AuditService
from vaultpass_backend.services.notification import NotificationService
from vaultpass_backend.core import constants

class SettingsService:
    """
    Service layer containing all business rules, validations, and operations for Settings.
    """

    @staticmethod
    async def get_or_create_settings(db: AsyncSession, user_id: uuid.UUID) -> UserSettings:
        """
        Retrieve settings for a user, creating a default settings entry if it does not exist.
        """
        settings = await SettingsRepository.get_by_user_id(db, user_id)
        if not settings:
            settings = UserSettings(user_id=user_id)
            settings = await SettingsRepository.create(db, settings)
        return settings

    @staticmethod
    async def get_profile(db: AsyncSession, user: User) -> ProfileSettingsResponse:
        """
        Retrieve profile details.
        """
        return ProfileSettingsResponse(
            full_name=user.full_name,
            email=user.email,
            created_at=user.created_at,
            last_login=user.last_login,
        )

    @staticmethod
    async def update_profile(
        db: AsyncSession,
        user: User,
        profile_data: ProfileSettingsUpdate,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ProfileSettingsResponse:
        """
        Update user profile information.
        """
        user.full_name = profile_data.full_name
        db.add(user)
        await db.flush()
        await db.refresh(user)

        # Log audit log
        await AuditService.log_action(
            db=db,
            user_id=user.id,
            action=constants.PROFILE_UPDATED,
            entity_type="USER",
            entity_id=user.id,
            description="User profile updated.",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Trigger notification
        await NotificationService.create_notification(
            db=db,
            user_id=user.id,
            title="Profile Updated",
            message="Your profile information was updated",
            type="SUCCESS",
        )

        return ProfileSettingsResponse(
            full_name=user.full_name,
            email=user.email,
            created_at=user.created_at,
            last_login=user.last_login,
        )

    @staticmethod
    async def get_security(db: AsyncSession, user_id: uuid.UUID) -> SecuritySettingsResponse:
        """
        Retrieve security settings.
        """
        settings = await SettingsService.get_or_create_settings(db, user_id)
        return SecuritySettingsResponse.model_validate(settings)

    @staticmethod
    async def update_security(
        db: AsyncSession,
        user_id: uuid.UUID,
        security_data: SecuritySettingsUpdate,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> SecuritySettingsResponse:
        """
        Update security settings.
        """
        settings = await SettingsService.get_or_create_settings(db, user_id)
        settings.two_factor_enabled = security_data.two_factor_enabled
        settings.auto_logout_enabled = security_data.auto_logout_enabled
        settings.session_timeout_minutes = security_data.session_timeout_minutes
        
        await SettingsRepository.save(db, settings)

        # Log audit log
        await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=constants.SECURITY_SETTINGS_UPDATED,
            entity_type="USER_SETTINGS",
            entity_id=settings.id,
            description="Security settings updated.",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Trigger notification
        await NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title="Security Settings Updated",
            message="Your security settings were updated",
            type="SUCCESS",
        )

        return SecuritySettingsResponse.model_validate(settings)

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User,
        password_data: ChangePasswordRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """
        Change user password.
        """
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )

        hashed_password = get_password_hash(password_data.new_password)
        user.password_hash = hashed_password
        db.add(user)
        await db.flush()

        # Log audit log
        await AuditService.log_action(
            db=db,
            user_id=user.id,
            action=constants.PASSWORD_CHANGED,
            entity_type="USER",
            entity_id=user.id,
            description="Account password changed.",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Trigger notification
        await NotificationService.create_notification(
            db=db,
            user_id=user.id,
            title="Password Changed",
            message="Your account password was changed",
            type="SUCCESS",
        )

    @staticmethod
    async def get_notifications(db: AsyncSession, user_id: uuid.UUID) -> NotificationSettingsResponse:
        """
        Retrieve notification settings.
        """
        settings = await SettingsService.get_or_create_settings(db, user_id)
        return NotificationSettingsResponse.model_validate(settings)

    @staticmethod
    async def update_notifications(
        db: AsyncSession,
        user_id: uuid.UUID,
        notifications_data: NotificationSettingsUpdate,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> NotificationSettingsResponse:
        """
        Update notification settings.
        """
        settings = await SettingsService.get_or_create_settings(db, user_id)
        settings.email_notifications = notifications_data.email_notifications
        settings.push_notifications = notifications_data.push_notifications
        settings.document_expiry_notifications = notifications_data.document_expiry_notifications
        settings.shared_access_notifications = notifications_data.shared_access_notifications
        settings.trusted_contact_notifications = notifications_data.trusted_contact_notifications
        settings.security_alert_notifications = notifications_data.security_alert_notifications
        settings.weekly_summary_notifications = notifications_data.weekly_summary_notifications

        await SettingsRepository.save(db, settings)

        # Log audit log
        await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=constants.NOTIFICATION_SETTINGS_UPDATED,
            entity_type="USER_SETTINGS",
            entity_id=settings.id,
            description="Notification settings updated.",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return NotificationSettingsResponse.model_validate(settings)

    @staticmethod
    async def get_privacy(db: AsyncSession, user_id: uuid.UUID) -> PrivacySettingsResponse:
        """
        Retrieve privacy settings.
        """
        settings = await SettingsService.get_or_create_settings(db, user_id)
        return PrivacySettingsResponse.model_validate(settings)

    @staticmethod
    async def update_privacy(
        db: AsyncSession,
        user_id: uuid.UUID,
        privacy_data: PrivacySettingsUpdate,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> PrivacySettingsResponse:
        """
        Update privacy settings.
        """
        settings = await SettingsService.get_or_create_settings(db, user_id)
        settings.allow_profile_visibility = privacy_data.allow_profile_visibility
        settings.allow_contact_visibility = privacy_data.allow_contact_visibility

        await SettingsRepository.save(db, settings)

        # Log audit log
        await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=constants.PRIVACY_SETTINGS_UPDATED,
            entity_type="USER_SETTINGS",
            entity_id=settings.id,
            description="Privacy settings updated.",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return PrivacySettingsResponse.model_validate(settings)

    @staticmethod
    async def get_reminders(db: AsyncSession, user_id: uuid.UUID) -> ReminderSettingsResponse:
        """
        Retrieve reminder settings.
        """
        settings = await SettingsService.get_or_create_settings(db, user_id)
        return ReminderSettingsResponse.model_validate(settings)

    @staticmethod
    async def update_reminders(
        db: AsyncSession,
        user_id: uuid.UUID,
        reminders_data: ReminderSettingsUpdate,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ReminderSettingsResponse:
        """
        Update reminder settings.
        """
        settings = await SettingsService.get_or_create_settings(db, user_id)
        settings.document_reminder_days = reminders_data.document_reminder_days

        await SettingsRepository.save(db, settings)

        # Log audit log
        await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=constants.REMINDER_SETTINGS_UPDATED,
            entity_type="USER_SETTINGS",
            entity_id=settings.id,
            description="Reminder settings updated.",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return ReminderSettingsResponse.model_validate(settings)

    @staticmethod
    async def get_account_info(db: AsyncSession, user: User) -> AccountInfoResponse:
        """
        Retrieve counts of documents, trusted contacts, and active shares.
        """
        doc_count_query = select(func.count(Document.id)).where(Document.owner_id == user.id)
        doc_res = await db.execute(doc_count_query)
        doc_count = doc_res.scalar() or 0

        contact_count_query = select(func.count(TrustedContact.id)).where(TrustedContact.owner_id == user.id)
        contact_res = await db.execute(contact_count_query)
        contact_count = contact_res.scalar() or 0

        share_count_query = select(func.count(DocumentShare.id)).where(
            DocumentShare.owner_id == user.id, DocumentShare.is_active == True
        )
        share_res = await db.execute(share_count_query)
        share_count = share_res.scalar() or 0

        return AccountInfoResponse(
            account_created=user.created_at,
            last_login=user.last_login,
            documents_count=doc_count,
            trusted_contacts_count=contact_count,
            active_shares_count=share_count,
        )

    @staticmethod
    async def export_settings(
        db: AsyncSession,
        user: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Dict[str, Any]:
        """
        Export all settings categories as a single dictionary.
        """
        settings = await SettingsService.get_or_create_settings(db, user.id)

        # Log audit log
        await AuditService.log_action(
            db=db,
            user_id=user.id,
            action=constants.ACCOUNT_SETTINGS_EXPORTED,
            entity_type="USER",
            entity_id=user.id,
            description="Account settings exported.",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return {
            "profile": {
                "full_name": user.full_name,
                "email": user.email,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            },
            "security": {
                "two_factor_enabled": settings.two_factor_enabled,
                "auto_logout_enabled": settings.auto_logout_enabled,
                "session_timeout_minutes": settings.session_timeout_minutes,
            },
            "notifications": {
                "email_notifications": settings.email_notifications,
                "push_notifications": settings.push_notifications,
                "document_expiry_notifications": settings.document_expiry_notifications,
                "shared_access_notifications": settings.shared_access_notifications,
                "trusted_contact_notifications": settings.trusted_contact_notifications,
                "security_alert_notifications": settings.security_alert_notifications,
                "weekly_summary_notifications": settings.weekly_summary_notifications,
            },
            "privacy": {
                "allow_profile_visibility": settings.allow_profile_visibility,
                "allow_contact_visibility": settings.allow_contact_visibility,
            },
            "reminders": {
                "document_reminder_days": settings.document_reminder_days,
            },
        }

    @staticmethod
    async def deactivate_account(
        db: AsyncSession,
        user: User,
        deactivate_data: DeactivateRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """
        Deactivate user account (soft delete only).
        """
        if not verify_password(deactivate_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )

        user.is_active = False
        db.add(user)
        await db.flush()

        # Log audit log
        await AuditService.log_action(
            db=db,
            user_id=user.id,
            action=constants.ACCOUNT_DEACTIVATED,
            entity_type="USER",
            entity_id=user.id,
            description="Account deactivated.",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Trigger notification
        await NotificationService.create_notification(
            db=db,
            user_id=user.id,
            title="Account Deactivated",
            message="Your account has been deactivated",
            type="WARNING",
        )
