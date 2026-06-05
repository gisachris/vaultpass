import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.core.dependencies import get_db, get_current_user
from vaultpass_backend.models.user import User
from vaultpass_backend.schemas.trusted_contact import (
    TrustedContactCreate,
    TrustedContactUpdate,
    TrustedContactResponse,
    TrustedContactCreateResponse,
    TrustedContactListResponse
)
from vaultpass_backend.services.trusted_contact import TrustedContactService

router = APIRouter(prefix="/v1/trusted-contacts", tags=["Trusted Contacts"])

@router.post(
    "",
    response_model=TrustedContactCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trusted contact",
    response_description="Created trusted contact details"
)
async def create(
    contact_data: TrustedContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new trusted contact for the authenticated user.
    - Checks for duplicate email per user (409 Conflict)
    """
    contact = await TrustedContactService.create_contact(
        db=db,
        owner_id=current_user.id,
        contact_data=contact_data
    )
    return TrustedContactCreateResponse(
        message="Trusted contact created successfully",
        data=TrustedContactResponse.model_validate(contact)
    )

@router.get(
    "",
    response_model=TrustedContactListResponse,
    status_code=status.HTTP_200_OK,
    summary="List trusted contacts",
    response_description="Paginated list of trusted contacts"
)
async def list_contacts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve user's trusted contacts with pagination.
    """
    items, total = await TrustedContactService.list_contacts(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )
    return TrustedContactListResponse(
        items=[TrustedContactResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )

@router.get(
    "/search",
    response_model=TrustedContactListResponse,
    status_code=status.HTTP_200_OK,
    summary="Search trusted contacts",
    response_description="Paginated search results of trusted contacts"
)
async def search(
    q: str = Query(..., min_length=1, description="Search query string"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search trusted contacts by full name, email, or relationship (case-insensitive).
    """
    items, total = await TrustedContactService.search_contacts(
        db=db,
        user_id=current_user.id,
        search_query=q,
        page=page,
        page_size=page_size
    )
    return TrustedContactListResponse(
        items=[TrustedContactResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )

@router.get(
    "/{contact_id}",
    response_model=TrustedContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a trusted contact",
    response_description="Trusted contact details"
)
async def get_single(
    contact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information of a specific trusted contact.
    - Enforces ownership constraints (403 Forbidden / 404 Not Found)
    """
    contact = await TrustedContactService.get_contact_by_id(
        db=db,
        contact_id=contact_id,
        user_id=current_user.id
    )
    return TrustedContactResponse.model_validate(contact)

@router.patch(
    "/{contact_id}",
    response_model=TrustedContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a trusted contact",
    response_description="Updated trusted contact details"
)
async def update(
    contact_id: uuid.UUID,
    update_data: TrustedContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Partially update a trusted contact.
    - Enforces ownership constraints and email uniqueness (403 Forbidden / 409 Conflict)
    """
    contact = await TrustedContactService.update_contact(
        db=db,
        contact_id=contact_id,
        user_id=current_user.id,
        update_data=update_data
    )
    return TrustedContactResponse.model_validate(contact)

@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a trusted contact",
    response_description="Deletion success confirmation message"
)
async def delete(
    contact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a trusted contact from the database.
    - Enforces ownership constraints (403 Forbidden)
    """
    await TrustedContactService.delete_contact(
        db=db,
        contact_id=contact_id,
        user_id=current_user.id
    )
    return {"message": "Trusted contact deleted successfully"}
