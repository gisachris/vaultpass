import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.core.dependencies import get_db, get_current_user
from vaultpass_backend.models.user import User
from vaultpass_backend.models.document import DocumentType
from vaultpass_backend.models.family_relationship import RelationshipType
from vaultpass_backend.schemas.family import (
    FamilyInvitationCreate,
    FamilyInvitationResponse,
    FamilyMemberResponse,
    FamilySummaryResponse,
    DependentDocumentsResponse
)
from vaultpass_backend.services.family import FamilyService

router = APIRouter(prefix="/family", tags=["Family Hub"])

@router.post(
    "/invitations",
    response_model=FamilyInvitationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new family invitation"
)
async def create_invitation(
    invitation_data: FamilyInvitationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invitation = await FamilyService.create_invitation(
        db=db,
        sender_id=current_user.id,
        schema=invitation_data
    )
    return FamilyInvitationResponse.model_validate(invitation)

@router.get(
    "/invitations/sent",
    response_model=List[FamilyInvitationResponse],
    status_code=status.HTTP_200_OK,
    summary="List sent family invitations"
)
async def list_sent_invitations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invitations = await FamilyService.get_sent_invitations(db=db, user_id=current_user.id)
    return [FamilyInvitationResponse.model_validate(inv) for inv in invitations]

@router.get(
    "/invitations/received",
    response_model=List[FamilyInvitationResponse],
    status_code=status.HTTP_200_OK,
    summary="List received family invitations"
)
async def list_received_invitations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invitations = await FamilyService.get_received_invitations(db=db, user_id=current_user.id)
    return [FamilyInvitationResponse.model_validate(inv) for inv in invitations]

@router.post(
    "/invitations/{id}/accept",
    response_model=FamilyInvitationResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept a family invitation"
)
async def accept_invitation(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invitation = await FamilyService.accept_invitation(db=db, relationship_id=id, user_id=current_user.id)
    return FamilyInvitationResponse.model_validate(invitation)

@router.post(
    "/invitations/{id}/decline",
    response_model=FamilyInvitationResponse,
    status_code=status.HTTP_200_OK,
    summary="Decline a family invitation"
)
async def decline_invitation(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invitation = await FamilyService.decline_invitation(db=db, relationship_id=id, user_id=current_user.id)
    return FamilyInvitationResponse.model_validate(invitation)

@router.delete(
    "/{relationshipId}",
    status_code=status.HTTP_200_OK,
    summary="Remove a family relationship"
)
async def remove_relationship(
    relationshipId: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await FamilyService.remove_relationship(db=db, relationship_id=relationshipId, user_id=current_user.id)
    return {"message": "Family relationship removed successfully"}

@router.get(
    "",
    response_model=List[FamilyMemberResponse],
    status_code=status.HTTP_200_OK,
    summary="List family members"
)
async def list_family_members(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    members = await FamilyService.get_family_members(db=db, user_id=current_user.id)
    return [FamilyMemberResponse.model_validate(m) for m in members]

@router.get(
    "/documents",
    response_model=List[DependentDocumentsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get guardian accessible documents grouped by dependent"
)
async def get_family_documents(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search filter for document title"),
    category: Optional[str] = Query(None, description="Alias for document type category filter"),
    dependent_name: Optional[str] = Query(None, description="Search filter for dependent name"),
    document_type: Optional[DocumentType] = Query(None, description="Filter by document type category"),
    date_uploaded: Optional[str] = Query(None, description="Filter by upload date (YYYY-MM-DD)"),
    relationship: Optional[RelationshipType] = Query(None, description="Filter by relationship type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await FamilyService.get_guardian_documents(
        db=db,
        guardian_id=current_user.id,
        page=page,
        limit=limit,
        search=search,
        category=category,
        dependent_name=dependent_name,
        document_type=document_type,
        date_uploaded=date_uploaded,
        relationship=relationship
    )

@router.get(
    "/summary",
    response_model=FamilySummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get family summary snapshot"
)
async def get_family_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await FamilyService.get_family_summary(db=db, user_id=current_user.id)
