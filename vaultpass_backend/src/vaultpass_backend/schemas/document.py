from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, List
from vaultpass_backend.models.document import DocumentType

class DocumentUpdateRequest(BaseModel):
    """
    Schema for updating document metadata.
    All fields are optional.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Title of the document")
    description: Optional[str] = Field(None, description="Optional description of the document")
    expiry_date: Optional[datetime] = Field(None, description="Optional expiration date of the document")
    document_type: Optional[DocumentType] = Field(None, description="Optional category of the document")

class DocumentCreateResponse(BaseModel):
    """
    Schema representing a created document's metadata response.
    """
    id: UUID
    owner_id: UUID
    title: str
    document_type: DocumentType
    description: Optional[str] = None
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    expiry_date: Optional[datetime] = None
    uploaded_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class DocumentDetailResponse(DocumentCreateResponse):
    """
    Schema representing full details of a document.
    Inherits fields from DocumentCreateResponse.
    """
    pass

class DocumentListResponse(BaseModel):
    """
    Paginated schema representing a list of documents.
    """
    items: List[DocumentCreateResponse]
    total: int
    page: int
    limit: int
