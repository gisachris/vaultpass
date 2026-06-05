import asyncio
import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.database.session import async_session_maker
from vaultpass_backend.models.document import Document
from vaultpass_backend.models.document_share import DocumentShare
from vaultpass_backend.models.notification import Notification, NotificationType
from vaultpass_backend.services.notification import NotificationService

logger = logging.getLogger("vaultpass")

class NotificationScheduler:
    """
    Background scheduler to scan the database and create notifications for:
    - Documents expiring in 30, 14, 7, 1 days.
    - Expired documents.
    - Expired document shares.
    """

    @staticmethod
    async def check_expiring_resources(db: AsyncSession) -> None:
        """
        Check documents and shares for expiry milestones and generate notifications.
        """
        now = datetime.now(timezone.utc)
        logger.info(f"NotificationScheduler: Starting check of expiring resources at {now.isoformat()}")

        # --- 1. CHECK DOCUMENTS ---
        # Fetch all documents with an expiry_date
        doc_query = select(Document).where(Document.expiry_date.isnot(None))
        doc_result = await db.execute(doc_query)
        documents = doc_result.scalars().all()

        for doc in documents:
            if doc.expiry_date is None:
                continue

            # Ensure expiry_date is timezone-aware
            expiry_date = doc.expiry_date
            if expiry_date.tzinfo is None:
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)

            if expiry_date <= now:
                # Document has expired. Check if we already sent an expiration error notification.
                existing_query = select(Notification).where(
                    and_(
                        Notification.user_id == doc.owner_id,
                        Notification.related_document_id == doc.id,
                        Notification.type == NotificationType.ERROR,
                        Notification.title.like("Document Expired:%")
                    )
                )
                existing_res = await db.execute(existing_query)
                if not existing_res.scalar_one_or_none():
                    logger.info(f"NotificationScheduler: Document {doc.id} ('{doc.title}') expired. Sending notification.")
                    await NotificationService.notify_document_expired(db, doc.owner_id, doc.id, doc.title)
            else:
                # Document is expiring. Calculate days remaining.
                # Use date comparison for clean day difference
                days_remaining = (expiry_date.date() - now.date()).days
                milestones = [30, 14, 7, 1]
                
                if days_remaining in milestones:
                    # Check if reminder already sent for this milestone
                    existing_query = select(Notification).where(
                        and_(
                            Notification.user_id == doc.owner_id,
                            Notification.related_document_id == doc.id,
                            Notification.type == NotificationType.WARNING,
                            Notification.title.like(f"Expiry Reminder ({days_remaining} days):%")
                        )
                    )
                    existing_res = await db.execute(existing_query)
                    if not existing_res.scalar_one_or_none():
                        logger.info(f"NotificationScheduler: Document {doc.id} ('{doc.title}') expires in {days_remaining} days. Sending notification.")
                        await NotificationService.notify_document_expiring(db, doc.owner_id, doc.id, doc.title, days_remaining)

        # --- 2. CHECK SHARED LINKS ---
        # Fetch active document shares with an expiry date
        share_query = select(DocumentShare).where(
            and_(
                DocumentShare.expires_at.isnot(None),
                DocumentShare.is_active == True
            )
        )
        share_result = await db.execute(share_query)
        shares = share_result.scalars().all()

        for share in shares:
            if share.expires_at is None:
                continue

            expires_at = share.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if expires_at <= now:
                # Share has expired. Check if notification already exists.
                existing_query = select(Notification).where(
                    and_(
                        Notification.user_id == share.owner_id,
                        Notification.related_share_id == share.id,
                        Notification.type == NotificationType.WARNING,
                        Notification.title.like("Shared Access Expired:%")
                    )
                )
                existing_res = await db.execute(existing_query)
                if not existing_res.scalar_one_or_none():
                    # Fetch document title
                    doc_query = select(Document.title).where(Document.id == share.document_id)
                    doc_title_res = await db.execute(doc_query)
                    doc_title = doc_title_res.scalar() or "document"

                    logger.info(f"NotificationScheduler: Share {share.id} for document '{doc_title}' has expired. Sending notification.")
                    await NotificationService.notify_share_expired(db, share.owner_id, share.id, doc_title, share.document_id)

    @staticmethod
    async def start_scheduler_loop() -> None:
        """
        Periodically wakes up every 24 hours to run the resource expiry checks.
        """
        logger.info("NotificationScheduler: Background loop started.")
        while True:
            try:
                async with async_session_maker() as db:
                    await NotificationScheduler.check_expiring_resources(db)
            except Exception as e:
                logger.error(f"NotificationScheduler: Error checking expiring resources: {e}", exc_info=True)
            
            # Sleep for 24 hours
            await asyncio.sleep(86400)
