import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from vaultpass_backend.models.family_relationship import RelationshipType, RelationshipStatus
from vaultpass_backend.schemas.document import DocumentCreateResponse

class FamilyUserMini(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str

    model_config = {
        "from_attributes": True
    }

class FamilyInvitationCreate(BaseModel):
    email: EmailStr = Field(..., description="Email of the family member to invite")
    relationship: RelationshipType = Field(..., description="Relationship type")
    notes: Optional[str] = Field(None, description="Optional notes for the invitation")

class FamilyInvitationResponse(BaseModel):
    id: uuid.UUID
    guardian_id: uuid.UUID
    dependent_id: uuid.UUID
    relationship: RelationshipType
    status: RelationshipStatus
    created_at: datetime
    accepted_at: Optional[datetime] = None
    invited_by: uuid.UUID
    notes: Optional[str] = None
    guardian: Optional[FamilyUserMini] = None
    dependent: Optional[FamilyUserMini] = None

    model_config = {
        "from_attributes": True
    }

class FamilyMemberResponse(BaseModel):
    id: uuid.UUID
    guardian: FamilyUserMini
    dependent: FamilyUserMini
    relationship: RelationshipType
    status: RelationshipStatus
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class FamilySummaryResponse(BaseModel):
    family_members: int
    guardian_count: int
    dependent_count: int
    accessible_documents: int
    pending_invitations: int

class DependentDocumentsResponse(BaseModel):
    dependent_id: uuid.UUID
    dependent_name: str
    relationship: RelationshipType
    documents: List[DocumentCreateResponse]
