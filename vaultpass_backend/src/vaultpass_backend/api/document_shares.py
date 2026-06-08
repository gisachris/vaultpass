import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.core.dependencies import get_db, get_current_user
from vaultpass_backend.models.user import User
from vaultpass_backend.schemas.document_share import (
    CreateDocumentShareRequest,
    UpdateDocumentShareRequest,
    DocumentShareResponse,
    SharedDocumentPublicResponse
)
from vaultpass_backend.services.document_share import DocumentShareService

router = APIRouter(prefix="/v1/shares", tags=["Shared Access"])
public_router = APIRouter(prefix="/public", tags=["Public Shared Access"])

# ================= PROTECTED ENDPOINTS =================

@router.post(
    "",
    response_model=DocumentShareResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document share link",
    response_description="Created document share details"
)
async def create(
    share_data: CreateDocumentShareRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a secure sharing link for a document.
    - User must own the document.
    - User must own the trusted contact.
    """
    share = await DocumentShareService.create_share(
        db=db,
        owner_id=current_user.id,
        share_data=share_data
    )
    return DocumentShareResponse.model_validate(share)

@router.get(
    "",
    response_model=List[DocumentShareResponse],
    status_code=status.HTTP_200_OK,
    summary="List user's document shares",
    response_description="List of all document shares created by user"
)
async def list_shares(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all document shares created by the authenticated user.
    """
    shares = await DocumentShareService.get_my_shares(db=db, user_id=current_user.id)
    return [DocumentShareResponse.model_validate(s) for s in shares]

@router.get(
    "/{share_id}",
    response_model=DocumentShareResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document share details",
    response_description="Document share metadata details"
)
async def get_details(
    share_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed metadata of a specific document share. Enforces ownership.
    """
    share = await DocumentShareService.get_share_by_id(
        db=db,
        share_id=share_id,
        user_id=current_user.id
    )
    return DocumentShareResponse.model_validate(share)

@router.put(
    "/{share_id}",
    response_model=DocumentShareResponse,
    status_code=status.HTTP_200_OK,
    summary="Update document share configuration",
    response_description="Updated document share details"
)
async def update(
    share_id: uuid.UUID,
    update_data: UpdateDocumentShareRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update expiration date or active status of a document share link. Enforces ownership.
    """
    share = await DocumentShareService.update_share(
        db=db,
        share_id=share_id,
        user_id=current_user.id,
        update_data=update_data
    )
    return DocumentShareResponse.model_validate(share)

@router.delete(
    "/{share_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a document share link",
    response_description="Deletion success confirmation message"
)
async def delete(
    share_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Permanently delete a document share link. Enforces ownership.
    """
    await DocumentShareService.delete_share(
        db=db,
        share_id=share_id,
        user_id=current_user.id
    )
    return {"message": "Document share deleted successfully"}

@router.patch(
    "/{share_id}/revoke",
    response_model=DocumentShareResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke a document share link",
    response_description="Revoked document share details"
)
async def revoke(
    share_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate a document share link immediately. Enforces ownership.
    """
    share = await DocumentShareService.revoke_share(
        db=db,
        share_id=share_id,
        user_id=current_user.id
    )
    return DocumentShareResponse.model_validate(share)

@router.patch(
    "/{share_id}/activate",
    response_model=DocumentShareResponse,
    status_code=status.HTTP_200_OK,
    summary="Reactivate a document share link",
    response_description="Reactivated document share details"
)
async def activate(
    share_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reactivate a previously deactivated document share link. Enforces ownership.
    """
    share = await DocumentShareService.activate_share(
        db=db,
        share_id=share_id,
        user_id=current_user.id
    )
    return DocumentShareResponse.model_validate(share)

@router.get(
    "/document/{document_id}",
    response_model=List[DocumentShareResponse],
    status_code=status.HTTP_200_OK,
    summary="List document shares associated with a document",
    response_description="List of document shares for the specified document"
)
async def list_shares_for_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all share links generated for a specific document. Enforces document ownership.
    """
    shares = await DocumentShareService.get_shares_for_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id
    )
    return [DocumentShareResponse.model_validate(s) for s in shares]


# ================= PUBLIC ENDPOINTS =================

@public_router.get(
    "/share/{token}",
    response_model=SharedDocumentPublicResponse,
    status_code=status.HTTP_200_OK,
    summary="Get shared document details public",
    response_description="Allowed document metadata details with secure temporary download URL"
)
async def get_public_share(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Access shared document details publicly using the secure access token.
    - Does not require authentication.
    - Validates token, status, expiration, and document existence.
    - Returns document metadata along with a secure 1-hour download URL.
    - Updates last accessed time.
    """
    metadata = await DocumentShareService.get_public_share_by_token(db=db, token=token)
    return SharedDocumentPublicResponse.model_validate(metadata)
