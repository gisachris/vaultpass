import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.models.audit_log import AuditLog


class AuditLogRepository:
    """
    Repository class encapsulating all database operations for AuditLog.
    Contains database logic only — no business logic.
    """

    @staticmethod
    async def create(db: AsyncSession, log: AuditLog) -> AuditLog:
        """
        Persist a new audit log entry.
        Uses add/flush/refresh instead of commit so callers that already
        have an open transaction are not affected.
        """
        db.add(log)
        await db.flush()
        await db.refresh(log)
        return log

    @staticmethod
    async def get_by_id(db: AsyncSession, log_id: uuid.UUID) -> Optional[AuditLog]:
        """
        Retrieve a single audit log entry by its UUID.
        """
        query = select(AuditLog).where(AuditLog.id == log_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_logs(
        db: AsyncSession,
        user_id: uuid.UUID,
        offset: int,
        limit: int,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
    ) -> List[AuditLog]:
        """
        Retrieve audit logs for a specific user with optional action/entity_type
        filters and pagination. Results are ordered newest-first.
        """
        query = select(AuditLog).where(AuditLog.user_id == user_id)

        if action:
            query = query.where(AuditLog.action == action.upper())
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type.upper())

        query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def count_user_logs(
        db: AsyncSession,
        user_id: uuid.UUID,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
    ) -> int:
        """
        Count audit logs owned by a specific user with optional filters.
        """
        query = (
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.user_id == user_id)
        )

        if action:
            query = query.where(AuditLog.action == action.upper())
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type.upper())

        result = await db.execute(query)
        return result.scalar_one()
