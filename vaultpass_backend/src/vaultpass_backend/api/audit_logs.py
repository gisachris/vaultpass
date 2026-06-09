import math
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.core.dependencies import get_db, get_current_user
from vaultpass_backend.models.user import User
from vaultpass_backend.schemas.audit_log import AuditLogResponse, AuditLogListResponse
from vaultpass_backend.services.audit_service import AuditService

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get(
    "",
    response_model=AuditLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's audit log",
    response_description="Paginated list of audit log entries for the authenticated user",
)
async def list_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    action: Optional[str] = Query(
        None, description="Filter by action (e.g. DOCUMENT_CREATED, LOGIN)"
    ),
    entity_type: Optional[str] = Query(
        None, description="Filter by entity type (e.g. DOCUMENT, USER)"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve audit log entries belonging to the currently authenticated user.
    Supports pagination and optional filtering by **action** and **entity_type**.

    Common action values: `LOGIN`, `REGISTER`, `LOGOUT`,
    `DOCUMENT_CREATED`, `DOCUMENT_UPDATED`, `DOCUMENT_DELETED`, `DOCUMENT_DOWNLOADED`,
    `CONTACT_CREATED`, `CONTACT_UPDATED`, `CONTACT_DELETED`,
    `DOCUMENT_SHARED`, `SHARE_REVOKED`.
    """
    items, total = await AuditService.get_user_logs(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
        action=action,
        entity_type=entity_type,
    )

    pages = math.ceil(total / limit) if total > 0 else 0

    return AuditLogListResponse(
        items=[AuditLogResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        pages=pages,
        limit=limit,
    )
