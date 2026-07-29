from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, computed_field
from typing import Optional, List

class TrustedContactCreate(BaseModel):
    """
    Schema for creating a new trusted contact.
    """
    full_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Optional full name of the contact. If omitted, resolved automatically: "
                     "the registered user's name if the email matches an existing account, "
                     "otherwise a placeholder derived from the email (replaced once the invitee registers)."
    )
    email: EmailStr = Field(
        ...,
        description="Unique email address for this owner"
    )
    phone_number: Optional[str] = Field(
        None,
        max_length=50,
        description="Optional phone number of the contact"
    )
    relationship: str = Field(
        ...,
        max_length=100,
        description="Relationship with the owner (e.g. Spouse, Sibling, Friend, Lawyer)"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional additional notes about the contact"
    )

class TrustedContactUpdate(BaseModel):
    """
    Schema for updating a trusted contact. All fields are optional.
    """
    full_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Full name of the contact"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Email address of the contact"
    )
    phone_number: Optional[str] = Field(
        None,
        max_length=50,
        description="Phone number of the contact"
    )
    relationship: Optional[str] = Field(
        None,
        max_length=100,
        description="Relationship with the owner"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional additional notes about the contact"
    )

class TrustedContactResponse(BaseModel):
    """
    Schema representing a trusted contact response.
    """
    id: UUID
    full_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    relationship: str
    notes: Optional[str] = None
    linked_user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @computed_field
    @property
    def is_registered_user(self) -> bool:
        """True when this contact is linked to a registered VaultPass account."""
        return self.linked_user_id is not None

    model_config = {
        "from_attributes": True
    }

class TrustedContactCreateResponse(BaseModel):
    """
    Schema for creation success response.
    """
    message: str = "Trusted contact created successfully"
    data: TrustedContactResponse

class TrustedContactListResponse(BaseModel):
    """
    Paginated schema representing a list of trusted contacts.
    """
    items: List[TrustedContactResponse]
    total: int
    page: int
    page_size: int
