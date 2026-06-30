import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class SummaryResponse(BaseModel):
    """Top-level dashboard summary cards."""
    total_documents: int
    trusted_contacts: int
    active_shares: int
    unread_notifications: int
    shared_with_me_count: int
    documents_previewed_count: int = 0
    documents_downloaded_count: int = 0
    family_members_count: int = 0
    dependents_count: int = 0
    guardian_accessible_documents_count: int = 0
    pending_family_invitations_count: int = 0


class DocumentHealthResponse(BaseModel):
    """Document health breakdown."""
    valid_documents: int
    expiring_soon: int
    expired_documents: int


class CategoryBreakdownResponse(BaseModel):
    """Single category entry for the pie chart."""
    category: str
    count: int


class ExpiringDocumentResponse(BaseModel):
    """A document that is expiring within the user's reminder window."""
    document_id: uuid.UUID
    document_name: str
    category: str
    expiry_date: datetime
    days_remaining: int


class RecentActivityResponse(BaseModel):
    """A single audit log entry shown in the activity feed."""
    action: str
    description: str
    created_at: datetime


class RecentNotificationResponse(BaseModel):
    """A recent notification shown in the dashboard panel."""
    id: uuid.UUID
    title: str
    message: str
    is_read: bool
    created_at: datetime


class SharedWithMeDocumentResponse(BaseModel):
    """A document shared with the user, shown in the dashboard."""
    share_id: uuid.UUID
    document_title: str
    owner_name: str
    shared_at: datetime


class AccountOverviewResponse(BaseModel):
    """Account-level metadata for the overview card."""
    account_created: datetime
    last_login: Optional[datetime]
    storage_used_mb: float


class DashboardResponse(BaseModel):
    """Complete dashboard payload returned by GET /api/dashboard/."""
    summary: SummaryResponse
    document_health: DocumentHealthResponse
    categories: List[CategoryBreakdownResponse]
    expiring_documents: List[ExpiringDocumentResponse]
    recent_activity: List[RecentActivityResponse]
    recent_notifications: List[RecentNotificationResponse]
    recent_shared_documents: List[SharedWithMeDocumentResponse]
    account_overview: AccountOverviewResponse
