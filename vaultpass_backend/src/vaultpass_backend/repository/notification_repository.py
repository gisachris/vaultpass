import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from vaultpass_backend.models.notification import Notification, NotificationType

class NotificationRepository:
    """
    Repository class encapsulating database operations for Notifications.
    Contains database logic only. No business logic.
    """

    @staticmethod
    async def create_notification(db: AsyncSession, notification: Notification) -> Notification:
        """
        Add a new notification to the database.
        """
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification

    @staticmethod
    async def get_notification_by_id(db: AsyncSession, notification_id: uuid.UUID) -> Optional[Notification]:
        """
        Retrieve a notification by its UUID.
        """
        query = select(Notification).where(Notification.id == notification_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user_id: uuid.UUID,
        offset: int,
        limit: int,
        is_read: Optional[bool] = None,
        notification_type: Optional[NotificationType] = None,
        sorting: Optional[str] = "desc"
    ) -> List[Notification]:
        """
        Retrieve notifications belonging to a specific user with pagination, filtering, and sorting.
        """
        query = select(Notification).where(Notification.user_id == user_id)
        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
        if notification_type is not None:
            query = query.where(Notification.type == notification_type)

        if sorting == "asc":
            query = query.order_by(Notification.created_at.asc())
        else:
            query = query.order_by(Notification.created_at.desc())

        query = query.offset(offset).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def count_user_notifications(
        db: AsyncSession,
        user_id: uuid.UUID,
        is_read: Optional[bool] = None,
        notification_type: Optional[NotificationType] = None
    ) -> int:
        """
        Count total notifications owned by a specific user with optional filters.
        """
        query = select(func.count()).select_from(Notification).where(Notification.user_id == user_id)
        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
        if notification_type is not None:
            query = query.where(Notification.type == notification_type)

        result = await db.execute(query)
        return result.scalar_one()

    @staticmethod
    async def get_unread_notifications(db: AsyncSession, user_id: uuid.UUID) -> List[Notification]:
        """
        Retrieve all unread notifications of a user.
        """
        query = select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def count_unread_notifications(db: AsyncSession, user_id: uuid.UUID) -> int:
        """
        Count unread notifications of a user.
        """
        query = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
        result = await db.execute(query)
        return result.scalar_one()

    @staticmethod
    async def mark_as_read(db: AsyncSession, notification: Notification) -> Notification:
        """
        Mark a notification as read.
        """
        notification.is_read = True
        await db.commit()
        await db.refresh(notification)
        return notification

    @staticmethod
    async def mark_as_unread(db: AsyncSession, notification: Notification) -> Notification:
        """
        Mark a notification as unread.
        """
        notification.is_read = False
        await db.commit()
        await db.refresh(notification)
        return notification

    @staticmethod
    async def mark_all_as_read(db: AsyncSession, user_id: uuid.UUID) -> None:
        """
        Mark all notifications as read for a specific user.
        """
        query = update(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).values(is_read=True)
        await db.execute(query)
        await db.commit()

    @staticmethod
    async def delete_notification(db: AsyncSession, notification: Notification) -> None:
        """
        Delete a single notification.
        """
        await db.delete(notification)
        await db.commit()

    @staticmethod
    async def delete_all_notifications(db: AsyncSession, user_id: uuid.UUID) -> None:
        """
        Delete all notifications for a specific user.
        """
        query = delete(Notification).where(Notification.user_id == user_id)
        await db.execute(query)
        await db.commit()
