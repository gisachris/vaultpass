import asyncio
import uuid
from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.models.document import Document
from vaultpass_backend.models.trusted_contact import TrustedContact
from vaultpass_backend.models.document_share import DocumentShare
from vaultpass_backend.models.user import User
from vaultpass_backend.repository.audit_log import AuditLogRepository
from vaultpass_backend.repository.notification_repository import NotificationRepository
from vaultpass_backend.repository.settings_repository import SettingsRepository
from vaultpass_backend.schemas.dashboard import (
    AccountOverviewResponse,
    CategoryBreakdownResponse,
    DashboardResponse,
    DocumentHealthResponse,
    ExpiringDocumentResponse,
    RecentActivityResponse,
    RecentNotificationResponse,
    SharedWithMeDocumentResponse,
    SummaryResponse,
)


class DashboardService:
    """
    Aggregation service for the VaultPass Dashboard.

    Collects data from all existing modules and composes a single
    DashboardResponse. Owns no data and creates no DB records.
    """

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    @staticmethod
    async def get_dashboard(db: AsyncSession, user: User) -> DashboardResponse:
        """
        Build the complete dashboard response for the authenticated user.

        Uses a two-phase asyncio.gather strategy:
          Phase 1 – fully independent queries run concurrently.
          Phase 2 – document-health / expiry queries that need reminder_days
                    (from Phase 1) run concurrently with each other.
        """
        # ── Phase 1: independent queries ──────────────────────────────── #
        (
            summary,
            reminder_days,
            recent_activity,
            recent_notifications,
            recent_shared_documents,
        ) = await asyncio.gather(
            DashboardService._get_summary(db, user.id),
            DashboardService._get_reminder_days(db, user.id),
            DashboardService._get_recent_activity(db, user.id),
            DashboardService._get_recent_notifications(db, user.id),
            DashboardService._get_recent_shared_with_me(db, user.id),
        )

        # ── Phase 2: depend on reminder_days ──────────────────────────── #
        (
            document_health,
            categories,
            expiring_documents,
            storage_mb,
        ) = await asyncio.gather(
            DashboardService._get_document_health(db, user.id, reminder_days),
            DashboardService._get_categories(db, user.id),
            DashboardService._get_expiring_documents(db, user.id, reminder_days),
            DashboardService._get_storage_used_mb(db, user.id),
        )

        account_overview = AccountOverviewResponse(
            account_created=user.created_at,
            last_login=user.last_login,
            storage_used_mb=storage_mb,
        )

        return DashboardResponse(
            summary=summary,
            document_health=document_health,
            categories=categories,
            expiring_documents=expiring_documents,
            recent_activity=recent_activity,
            recent_notifications=recent_notifications,
            recent_shared_documents=recent_shared_documents,
            account_overview=account_overview,
        )

    # ------------------------------------------------------------------ #
    # Phase 1 helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    async def _get_summary(db: AsyncSession, user_id: uuid.UUID) -> SummaryResponse:
        """Fetch the summary card counts concurrently."""
        from vaultpass_backend.services.notification import NotificationService
        from vaultpass_backend.services.family import asyncio_gather_summary_counts

        (
            total_documents,
            trusted_contacts,
            active_shares,
            unread_notifications,
            shared_with_me_count,
            documents_previewed_count,
            documents_downloaded_count,
            family_counts,
        ) = await asyncio.gather(
            DashboardService._count_documents(db, user_id),
            DashboardService._count_trusted_contacts(db, user_id),
            DashboardService._count_active_shares(db, user_id),
            NotificationService.get_unread_count(db, user_id),
            DashboardService._count_received_shares(db, user_id),
            DashboardService._count_previews(db, user_id),
            DashboardService._count_downloads(db, user_id),
            asyncio_gather_summary_counts(db, user_id)
        )

        family_members, guardian_count, dependent_count, pending_invitations, accessible_docs = family_counts

        return SummaryResponse(
            total_documents=total_documents,
            trusted_contacts=trusted_contacts,
            active_shares=active_shares,
            unread_notifications=unread_notifications,
            shared_with_me_count=shared_with_me_count,
            documents_previewed_count=documents_previewed_count,
            documents_downloaded_count=documents_downloaded_count,
            family_members_count=family_members,
            dependents_count=dependent_count,
            guardian_accessible_documents_count=accessible_docs,
            pending_family_invitations_count=pending_invitations,
        )

    @staticmethod
    async def _get_reminder_days(db: AsyncSession, user_id: uuid.UUID) -> int:
        """Return the user's configured reminder window (default 30 days)."""
        settings = await SettingsRepository.get_by_user_id(db, user_id)
        if settings:
            return settings.document_reminder_days
        return 30

    @staticmethod
    async def _get_recent_activity(
        db: AsyncSession, user_id: uuid.UUID
    ) -> List[RecentActivityResponse]:
        """Return the 20 most recent audit log entries for the user."""
        logs = await AuditLogRepository.get_user_logs(
            db=db,
            user_id=user_id,
            offset=0,
            limit=20,
        )
        return [
            RecentActivityResponse(
                action=log.action,
                description=log.description,
                created_at=log.created_at,
            )
            for log in logs
        ]

    @staticmethod
    async def _get_recent_notifications(
        db: AsyncSession, user_id: uuid.UUID
    ) -> List[RecentNotificationResponse]:
        """Return the 10 most recent notifications for the user."""
        notifications = await NotificationRepository.get_user_notifications(
            db=db,
            user_id=user_id,
            offset=0,
            limit=10,
            sorting="desc",
        )
        return [
            RecentNotificationResponse(
                id=n.id,
                title=n.title,
                message=n.message,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            for n in notifications
        ]

    # ------------------------------------------------------------------ #
    # Phase 2 helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    async def _get_document_health(
        db: AsyncSession, user_id: uuid.UUID, reminder_days: int
    ) -> DocumentHealthResponse:
        """
        Count valid, expiring-soon, and expired documents.

        valid_documents  – no expiry date, or expiry date is in the future
        expiring_soon    – expiry date within [now, now + reminder_days]
        expired_documents – expiry date is in the past
        """
        now = datetime.now(timezone.utc)
        from datetime import timedelta
        reminder_cutoff = now + timedelta(days=reminder_days)

        base = Document.owner_id == user_id

        valid_q = select(func.count()).select_from(Document).where(
            and_(base, (Document.expiry_date == None) | (Document.expiry_date > now))
        )
        expiring_q = select(func.count()).select_from(Document).where(
            and_(base, Document.expiry_date != None,
                 Document.expiry_date > now,
                 Document.expiry_date <= reminder_cutoff)
        )
        expired_q = select(func.count()).select_from(Document).where(
            and_(base, Document.expiry_date != None, Document.expiry_date <= now)
        )

        valid_r, expiring_r, expired_r = await asyncio.gather(
            db.execute(valid_q),
            db.execute(expiring_q),
            db.execute(expired_q),
        )

        return DocumentHealthResponse(
            valid_documents=valid_r.scalar() or 0,
            expiring_soon=expiring_r.scalar() or 0,
            expired_documents=expired_r.scalar() or 0,
        )

    @staticmethod
    async def _get_categories(
        db: AsyncSession, user_id: uuid.UUID
    ) -> List[CategoryBreakdownResponse]:
        """Group documents by category, sorted descending by count."""
        query = (
            select(Document.document_type, func.count().label("count"))
            .where(Document.owner_id == user_id)
            .group_by(Document.document_type)
            .order_by(func.count().desc())
        )
        result = await db.execute(query)
        rows = result.all()
        return [
            CategoryBreakdownResponse(
                category=row.document_type.value if hasattr(row.document_type, "value") else str(row.document_type),
                count=row.count,
            )
            for row in rows
        ]

    @staticmethod
    async def _get_expiring_documents(
        db: AsyncSession, user_id: uuid.UUID, reminder_days: int
    ) -> List[ExpiringDocumentResponse]:
        """
        Return the top 10 documents expiring within the reminder window,
        sorted soonest-expiry first. Includes computed days_remaining.
        """
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        reminder_cutoff = now + timedelta(days=reminder_days)

        query = (
            select(Document)
            .where(
                and_(
                    Document.owner_id == user_id,
                    Document.expiry_date != None,
                    Document.expiry_date > now,
                    Document.expiry_date <= reminder_cutoff,
                )
            )
            .order_by(Document.expiry_date.asc())
            .limit(10)
        )
        result = await db.execute(query)
        docs = list(result.scalars().all())

        items = []
        for doc in docs:
            expiry = doc.expiry_date
            # Normalise timezone for subtraction
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            days_remaining = max(0, (expiry - now).days)
            items.append(
                ExpiringDocumentResponse(
                    document_id=doc.id,
                    document_name=doc.title,
                    category=doc.document_type.value if hasattr(doc.document_type, "value") else str(doc.document_type),
                    expiry_date=expiry,
                    days_remaining=days_remaining,
                )
            )
        return items

    @staticmethod
    async def _get_storage_used_mb(db: AsyncSession, user_id: uuid.UUID) -> float:
        """
        Sum all document file sizes for the user and return the total in MB
        rounded to one decimal place.
        """
        query = select(func.sum(Document.file_size)).where(Document.owner_id == user_id)
        result = await db.execute(query)
        total_bytes = result.scalar() or 0
        return round(total_bytes / (1024 * 1024), 1)

    # ------------------------------------------------------------------ #
    # Scalar count helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    async def _count_documents(db: AsyncSession, user_id: uuid.UUID) -> int:
        result = await db.execute(
            select(func.count()).select_from(Document).where(Document.owner_id == user_id)
        )
        return result.scalar() or 0

    @staticmethod
    async def _count_trusted_contacts(db: AsyncSession, user_id: uuid.UUID) -> int:
        result = await db.execute(
            select(func.count()).select_from(TrustedContact).where(TrustedContact.owner_id == user_id)
        )
        return result.scalar() or 0

    @staticmethod
    async def _count_active_shares(db: AsyncSession, user_id: uuid.UUID) -> int:
        result = await db.execute(
            select(func.count()).select_from(DocumentShare).where(
                and_(DocumentShare.owner_id == user_id, DocumentShare.is_active == True)
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def _count_received_shares(db: AsyncSession, user_id: uuid.UUID) -> int:
        """Count all document shares received by this user (they are the recipient)."""
        from vaultpass_backend.repository.document_share import DocumentShareRepository
        return await DocumentShareRepository.count_received_shares(db, user_id)

    @staticmethod
    async def _get_recent_shared_with_me(
        db: AsyncSession, user_id: uuid.UUID
    ) -> List[SharedWithMeDocumentResponse]:
        """Return the 5 most recently received shared documents for the dashboard panel."""
        from vaultpass_backend.repository.document_share import DocumentShareRepository
        from sqlalchemy.orm import selectinload

        shares = await DocumentShareRepository.get_received_shares(db, user_id)
        items = []
        for s in shares[:5]:
            doc = s.document
            owner = s.owner
            items.append(
                SharedWithMeDocumentResponse(
                    share_id=s.id,
                    document_title=doc.title if doc else "Unknown",
                    owner_name=owner.full_name if owner else "Unknown",
                    shared_at=s.created_at,
                )
            )
        return items

    @staticmethod
    async def _count_previews(db: AsyncSession, user_id: uuid.UUID) -> int:
        from vaultpass_backend.models.audit_log import AuditLog
        result = await db.execute(
            select(func.count()).select_from(AuditLog).where(
                and_(AuditLog.user_id == user_id, AuditLog.action == "DOCUMENT_PREVIEWED")
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def _count_downloads(db: AsyncSession, user_id: uuid.UUID) -> int:
        from vaultpass_backend.models.audit_log import AuditLog
        result = await db.execute(
            select(func.count()).select_from(AuditLog).where(
                and_(AuditLog.user_id == user_id, AuditLog.action == "DOCUMENT_DOWNLOADED")
            )
        )
        return result.scalar() or 0
