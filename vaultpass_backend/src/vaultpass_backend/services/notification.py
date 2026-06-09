import uuid
from typing import Tuple, List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.models.notification import Notification, NotificationType
from vaultpass_backend.repository.notification_repository import NotificationRepository

class NotificationService:
    """
    Service layer containing all business rules, validations, ownership enforcement,
    and automatic notification generation helpers.
    """

    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: uuid.UUID,
        title: str,
        message: str,
        type: NotificationType,
        related_document_id: Optional[uuid.UUID] = None,
        related_contact_id: Optional[uuid.UUID] = None,
        related_share_id: Optional[uuid.UUID] = None
    ) -> Optional[Notification]:
        """
        Internal helper to construct and save a notification.
        Filters notification creation based on user preference settings.
        """
        # Check settings
        from vaultpass_backend.repository.settings_repository import SettingsRepository
        settings = await SettingsRepository.get_by_user_id(db, user_id)
        if settings:
            title_lower = title.lower()
            if "expiry" in title_lower or "expired" in title_lower:
                if not settings.document_expiry_notifications:
                    return None
            elif "shared" in title_lower or "share" in title_lower or "accessed" in title_lower:
                if not settings.shared_access_notifications:
                    return None
            elif "contact" in title_lower:
                if not settings.trusted_contact_notifications:
                    return None
            elif any(k in title_lower for k in ["security", "password", "profile", "deactivated", "emergency"]):
                if not settings.security_alert_notifications:
                    return None

        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            related_document_id=related_document_id,
            related_contact_id=related_contact_id,
            related_share_id=related_share_id,
            is_read=False
        )
        return await NotificationRepository.create_notification(db, notification)

    @staticmethod
    async def get_notification(
        db: AsyncSession,
        notification_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Notification:
        """
        Retrieve a single notification, enforcing ownership.
        """
        notification = await NotificationRepository.get_notification_by_id(db, notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        if notification.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this notification"
            )
        return notification

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        limit: int = 20,
        is_read: Optional[bool] = None,
        type: Optional[NotificationType] = None,
        sorting: Optional[str] = "desc"
    ) -> Tuple[List[Notification], int]:
        """
        Retrieve paginated list of notifications for the user with filters and sorting.
        """
        if page < 1:
            page = 1
        if limit < 1:
            limit = 20

        offset = (page - 1) * limit
        items = await NotificationRepository.get_user_notifications(
            db=db,
            user_id=user_id,
            offset=offset,
            limit=limit,
            is_read=is_read,
            notification_type=type,
            sorting=sorting
        )
        total = await NotificationRepository.count_user_notifications(
            db=db,
            user_id=user_id,
            is_read=is_read,
            notification_type=type
        )
        return items, total

    @staticmethod
    async def mark_read(
        db: AsyncSession,
        notification_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Notification:
        """
        Mark a notification as read.
        """
        notification = await NotificationService.get_notification(db, notification_id, user_id)
        return await NotificationRepository.mark_as_read(db, notification)

    @staticmethod
    async def mark_unread(
        db: AsyncSession,
        notification_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Notification:
        """
        Mark a notification as unread.
        """
        notification = await NotificationService.get_notification(db, notification_id, user_id)
        return await NotificationRepository.mark_as_unread(db, notification)

    @staticmethod
    async def mark_all_read(db: AsyncSession, user_id: uuid.UUID) -> None:
        """
        Mark all notifications of a user as read.
        """
        await NotificationRepository.mark_all_as_read(db, user_id)

    @staticmethod
    async def delete_notification(
        db: AsyncSession,
        notification_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> None:
        """
        Delete a single notification.
        """
        notification = await NotificationService.get_notification(db, notification_id, user_id)
        await NotificationRepository.delete_notification(db, notification)

    @staticmethod
    async def delete_all_notifications(db: AsyncSession, user_id: uuid.UUID) -> None:
        """
        Delete all notifications belonging to the user.
        """
        await NotificationRepository.delete_all_notifications(db, user_id)

    @staticmethod
    async def get_unread_count(db: AsyncSession, user_id: uuid.UUID) -> int:
        """
        Count total unread notifications for the user.
        """
        return await NotificationRepository.count_unread_notifications(db, user_id)


    # ================= AUTOMATIC EVENT HOOKS =================

    # 1. Document Events
    @staticmethod
    async def notify_document_uploaded(db: AsyncSession, owner_id: uuid.UUID, doc_id: uuid.UUID, doc_title: str) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Document Uploaded",
            message=f"{doc_title} uploaded successfully.",
            type=NotificationType.SUCCESS,
            related_document_id=doc_id
        )

    @staticmethod
    async def notify_document_updated(db: AsyncSession, owner_id: uuid.UUID, doc_id: uuid.UUID, doc_title: str) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Document Updated",
            message=f"{doc_title} updated successfully.",
            type=NotificationType.SUCCESS,
            related_document_id=doc_id
        )

    @staticmethod
    async def notify_document_deleted(db: AsyncSession, owner_id: uuid.UUID, doc_title: str) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Document Deleted",
            message=f"{doc_title} removed from vault.",
            type=NotificationType.INFO
        )

    @staticmethod
    async def notify_document_expiring(db: AsyncSession, owner_id: uuid.UUID, doc_id: uuid.UUID, doc_title: str, days: int) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title=f"Expiry Reminder ({days} days): {doc_title}",
            message=f"{doc_title} expires in {days} days.",
            type=NotificationType.WARNING,
            related_document_id=doc_id
        )

    @staticmethod
    async def notify_document_expired(db: AsyncSession, owner_id: uuid.UUID, doc_id: uuid.UUID, doc_title: str) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title=f"Document Expired: {doc_title}",
            message=f"{doc_title} has expired.",
            type=NotificationType.ERROR,
            related_document_id=doc_id
        )

    # 2. Trusted Contact Events
    @staticmethod
    async def notify_contact_added(db: AsyncSession, owner_id: uuid.UUID, contact_id: uuid.UUID, contact_name: str) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Trusted Contact Added",
            message=f"{contact_name} added as trusted contact.",
            type=NotificationType.INFO,
            related_contact_id=contact_id
        )

    @staticmethod
    async def notify_contact_updated(db: AsyncSession, owner_id: uuid.UUID, contact_id: uuid.UUID, contact_name: str) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Trusted Contact Updated",
            message=f"Trusted contact information updated.",
            type=NotificationType.INFO,
            related_contact_id=contact_id
        )

    @staticmethod
    async def notify_contact_deleted(db: AsyncSession, owner_id: uuid.UUID, contact_name: str) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Trusted Contact Deleted",
            message=f"Trusted contact removed successfully.",
            type=NotificationType.INFO
        )

    # 3. Shared Access Events
    @staticmethod
    async def notify_document_shared(
        db: AsyncSession,
        owner_id: uuid.UUID,
        share_id: uuid.UUID,
        doc_title: str,
        contact_name: str,
        doc_id: uuid.UUID,
        contact_id: uuid.UUID
    ) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Document Shared",
            message=f"{doc_title} shared with {contact_name}.",
            type=NotificationType.SUCCESS,
            related_document_id=doc_id,
            related_contact_id=contact_id,
            related_share_id=share_id
        )

    @staticmethod
    async def notify_share_revoked(
        db: AsyncSession,
        owner_id: uuid.UUID,
        share_id: uuid.UUID,
        doc_title: str,
        doc_id: uuid.UUID,
        contact_id: uuid.UUID
    ) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Share Access Revoked",
            message=f"Access revoked for {doc_title}.",
            type=NotificationType.INFO,
            related_document_id=doc_id,
            related_contact_id=contact_id,
            related_share_id=share_id
        )

    @staticmethod
    async def notify_share_expired(db: AsyncSession, owner_id: uuid.UUID, share_id: uuid.UUID, doc_title: str, doc_id: uuid.UUID) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title=f"Shared Access Expired: {doc_title}",
            message=f"Shared access link has expired.",
            type=NotificationType.WARNING,
            related_document_id=doc_id,
            related_share_id=share_id
        )

    @staticmethod
    async def notify_share_accessed(db: AsyncSession, owner_id: uuid.UUID, share_id: uuid.UUID, doc_title: str, contact_name: str, doc_id: uuid.UUID) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Shared Document Accessed",
            message=f"{contact_name} accessed shared {doc_title}.",
            type=NotificationType.INFO,
            related_document_id=doc_id,
            related_share_id=share_id
        )

    # 4. Future Emergency Events
    @staticmethod
    async def notify_emergency_request(db: AsyncSession, owner_id: uuid.UUID, contact_name: str) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Emergency Access Requested",
            message=f"{contact_name} requested emergency access.",
            type=NotificationType.INFO
        )

    @staticmethod
    async def notify_emergency_approved(db: AsyncSession, owner_id: uuid.UUID, contact_name: str) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Emergency Access Approved",
            message=f"Emergency access for {contact_name} has been approved.",
            type=NotificationType.SUCCESS
        )

    @staticmethod
    async def notify_emergency_access_used(db: AsyncSession, owner_id: uuid.UUID, contact_name: str) -> Notification:
        return await NotificationService.create_notification(
            db=db,
            user_id=owner_id,
            title="Emergency Access Used",
            message=f"{contact_name} used emergency access to view vault.",
            type=NotificationType.WARNING
        )
