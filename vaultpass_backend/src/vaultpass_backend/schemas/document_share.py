from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
from vaultpass_backend.models.document import DocumentType

class CreateDocumentShareRequest(BaseModel):
    """
    Schema for creating a document share link.
    """
    document_id: UUID = Field(..., description="UUID of the document to share")
    contact_id: UUID = Field(..., description="UUID of the trusted contact to share with")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date of the share link")
    access_level: Optional[str] = Field(None, description="Access level for internal shares")
    allow_download: bool = Field(True, description="Whether downloading is allowed for this share")
    password: Optional[str] = Field(None, description="Optional password protection for external shares")

class UpdateDocumentShareRequest(BaseModel):
    """
    Schema for updating document share properties.
    """
    expires_at: Optional[datetime] = Field(None, description="Optional updated expiration date of the share link")
    is_active: Optional[bool] = Field(None, description="Optional active status of the share link")

class DocumentShareResponse(BaseModel):
    """
    Schema representing a document share response details.
    """
    id: UUID
    document_id: UUID
    contact_id: UUID
    owner_id: UUID
    access_token: str
    share_link: str
    is_active: bool
    recipient_user_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    access_level: Optional[str] = None
    allow_download: bool = True

    model_config = {
        "from_attributes": True
    }

class SharedDocumentPublicResponse(BaseModel):
    """
    Schema representing public document metadata response.
    Does NOT return private owner details.
    """
    title: str
    document_type: DocumentType
    created_at: datetime
    expiry_date: Optional[datetime] = None
    download_url: Optional[str] = None
    password_required: bool = False
    allow_download: bool = True

class SharedWithMeResponse(BaseModel):
    """
    Schema for a document shared with the authenticated user (list view).
    """
    share_id: UUID
    document_id: UUID
    document_title: str
    document_type: str
    owner_name: str
    shared_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool
    access_level: Optional[str] = None
    allow_download: bool = True

    model_config = {
        "from_attributes": True
    }

class SharedWithMeDetailResponse(SharedWithMeResponse):
    """
    Schema for a single received share (detail view).
    Extends the list view with additional fields.
    """
    owner_id: UUID
    contact_id: UUID
    last_accessed_at: Optional[datetime] = None
