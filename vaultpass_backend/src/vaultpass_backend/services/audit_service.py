import uuid
import logging
from typing import Optional, Tuple, List, Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.models.audit_log import AuditLog
from vaultpass_backend.repository.audit_log import AuditLogRepository

logger = logging.getLogger("vaultpass")


class AuditService:
    """
    Service layer for audit logging.

    Provides:
      - log_action(): fire-and-forget helper called by other services/routers
        to record a security or system event without interrupting the main flow.
      - get_user_logs(): paginated query with optional filters for the API.
    """

    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: uuid.UUID,
        action: str,
        entity_type: str,
        description: str,
        entity_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        Write a single audit log entry.

        Failures are caught and logged as warnings so a logging error never
        causes the parent request to fail.
        """
        try:
            log = AuditLog(
                user_id=user_id,
                action=action.upper(),
                entity_type=entity_type.upper(),
                entity_id=entity_id,
                description=description,
                metadata_=metadata,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            await AuditLogRepository.create(db, log)
        except Exception as exc:  # pragma: no cover
            logger.warning(
                "Failed to write audit log [action=%s entity=%s user=%s]: %s",
                action,
                entity_type,
                user_id,
                exc,
            )

    @staticmethod
    async def get_user_logs(
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        limit: int = 20,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
    ) -> Tuple[List[AuditLog], int]:
        """
        Return paginated audit logs for the authenticated user with optional
        action/entity_type filters.
        """
        if page < 1:
            page = 1
        if limit < 1:
            limit = 20

        offset = (page - 1) * limit

        items = await AuditLogRepository.get_user_logs(
            db=db,
            user_id=user_id,
            offset=offset,
            limit=limit,
            action=action,
            entity_type=entity_type,
        )
        total = await AuditLogRepository.count_user_logs(
            db=db,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
        )
        return items, total
