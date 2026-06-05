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
    expires_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

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
    download_url: str
