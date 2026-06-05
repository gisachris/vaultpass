import uuid
import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.core.dependencies import get_db, get_current_user
from vaultpass_backend.models.user import User
from vaultpass_backend.models.notification import NotificationType
from vaultpass_backend.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
)
from vaultpass_backend.services.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get(
    "",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's notifications",
    response_description="Paginated list of user notifications"
)
async def list_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    is_read: Optional[bool] = Query(None, description="Filter by read/unread status"),
    type: Optional[NotificationType] = Query(None, description="Filter by notification type"),
    sorting: Optional[str] = Query("desc", pattern="^(asc|desc)$", description="Sort by created_at: asc or desc"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all notifications owned by the currently authenticated user.
    Supports pagination, filtering by is_read/type, and custom sorting by created_at.
    """
    items, total = await NotificationService.get_user_notifications(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
        is_read=is_read,
        type=type,
        sorting=sorting
    )

    pages = math.ceil(total / limit) if total > 0 else 0

    return NotificationListResponse(
        items=[NotificationResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        pages=pages,
        limit=limit
    )

@router.get(
    "/unread-count",
    status_code=status.HTTP_200_OK,
    summary="Get count of unread notifications",
    response_description="JSON count of unread notifications"
)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the total count of unread notifications for the authenticated user.
    """
    count = await NotificationService.get_unread_count(db=db, user_id=current_user.id)
    return {"unread_count": count}

@router.patch(
    "/read-all",
    status_code=status.HTTP_200_OK,
    summary="Mark all notifications as read",
    response_description="Bulk action confirmation"
)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all notifications of the authenticated user as read.
    """
    await NotificationService.mark_all_read(db=db, user_id=current_user.id)
    return {"message": "All notifications marked as read"}

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single notification details",
    response_description="Notification metadata details"
)
async def get_notification(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve details of a specific notification owned by the user.
    """
    notification = await NotificationService.get_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    return NotificationResponse.model_validate(notification)

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark notification as read",
    response_description="Updated notification"
)
async def mark_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a specific notification as read.
    """
    notification = await NotificationService.mark_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    return NotificationResponse.model_validate(notification)

@router.patch(
    "/{notification_id}/unread",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark notification as unread",
    response_description="Updated notification"
)
async def mark_unread(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a specific notification as unread.
    """
    notification = await NotificationService.mark_unread(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    return NotificationResponse.model_validate(notification)

@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a single notification",
    response_description="Deletion success confirmation"
)
async def delete_notification(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific notification.
    """
    await NotificationService.delete_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    return {"message": "Notification deleted successfully"}

@router.delete(
    "",
    status_code=status.HTTP_200_OK,
    summary="Delete all notifications",
    response_description="Bulk deletion success confirmation"
)
async def delete_all_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete all notifications belonging to the authenticated user.
    """
    await NotificationService.delete_all_notifications(db=db, user_id=current_user.id)
    return {"message": "All notifications deleted successfully"}
