from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, List
from vaultpass_backend.models.notification import NotificationType

class CreateNotificationRequest(BaseModel):
    """
    Schema for creating a notification (mainly for internal helpers).
    """
    title: str = Field(..., max_length=255, description="Title of the notification")
    message: str = Field(..., description="Message details of the notification")
    type: NotificationType = Field(..., description="Type of the notification (INFO, SUCCESS, WARNING, ERROR)")
    related_document_id: Optional[UUID] = Field(None, description="Optional related document UUID")
    related_contact_id: Optional[UUID] = Field(None, description="Optional related trusted contact UUID")
    related_share_id: Optional[UUID] = Field(None, description="Optional related document share UUID")

class UpdateNotificationRequest(BaseModel):
    """
    Schema for updating a notification.
    """
    is_read: bool = Field(..., description="Read/unread status of the notification")

class NotificationResponse(BaseModel):
    """
    Schema representing a notification response details.
    """
    id: UUID
    title: str
    message: str
    type: NotificationType
    is_read: bool
    related_document_id: Optional[UUID] = None
    related_contact_id: Optional[UUID] = None
    related_share_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class NotificationListResponse(BaseModel):
    """
    Paginated schema representing a list of notifications.
    """
    items: List[NotificationResponse]
    total: int
    page: int
    pages: int
    limit: int
