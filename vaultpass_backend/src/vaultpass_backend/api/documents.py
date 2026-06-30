import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.core.dependencies import get_db, get_current_user
from vaultpass_backend.models.document import DocumentType
from vaultpass_backend.models.user import User
from vaultpass_backend.schemas.document import (
    DocumentCreateResponse,
    DocumentUpdateRequest,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentPreviewResponse,
    DocumentDownloadResponse,
)
from vaultpass_backend.services.document_service import (
    upload_document,
    get_document_by_id,
    get_documents,
    generate_download_link,
    update_document,
    delete_document,
)
from vaultpass_backend.services.document_access_service import DocumentAccessService

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post(
    "/upload",
    response_model=DocumentCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    response_description="Created document metadata"
)
async def upload(
    file: UploadFile = File(..., description="The document file (PDF, PNG, JPG, JPEG)"),
    title: str = Form(..., min_length=1, max_length=255, description="Title of the document"),
    document_type: DocumentType = Form(..., description="Category type of the document"),
    description: Optional[str] = Form(None, description="Optional description"),
    expiry_date: Optional[datetime] = Form(None, description="Optional expiration date"),
    guardian_visibility: bool = Form(True, description="Whether guardians may automatically access this document"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document:
    - User must be authenticated
    - Accepted types: PDF, PNG, JPG, JPEG
    - Maximum size: 10MB
    - Stores file in Supabase Storage and metadata in PostgreSQL
    """
    doc = await upload_document(
        db=db,
        owner_id=current_user.id,
        file=file,
        title=title,
        document_type=document_type,
        description=description,
        expiry_date=expiry_date,
        guardian_visibility=guardian_visibility
    )
    return DocumentCreateResponse.model_validate(doc)

@router.get(
    "",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's documents",
    response_description="Paginated list of user documents"
)
async def list_docs(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search filter for title"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all documents owned by the currently authenticated user.
    Supports pagination and case-insensitive search on title.
    """
    items, total = await get_documents(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
        search=search
    )
    
    items_response = []
    for item in items:
        resp = DocumentCreateResponse.model_validate(item)
        resp.permission_source = "OWNER"
        items_response.append(resp)
        
    return DocumentListResponse(
        items=items_response,
        total=total,
        page=page,
        limit=limit
    )

@router.get(
    "/{id}",
    response_model=DocumentDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document details",
    response_description="Document metadata details"
)
async def get_details(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed metadata of a specific document owned by the user or accessed via guardianship.
    """
    doc = await get_document_by_id(db=db, doc_id=id, user_id=current_user.id, allow_guardian=True)
    res = DocumentDetailResponse.model_validate(doc)
    if doc.owner_id == current_user.id:
        res.permission_source = "OWNER"
    else:
        # Check if guardian
        from vaultpass_backend.repository.family import FamilyRepository
        is_guardian = await FamilyRepository.check_is_guardian(db, guardian_id=current_user.id, dependent_id=doc.owner_id)
        if is_guardian:
            res.permission_source = "GUARDIAN"
        else:
            res.permission_source = "SHARED"
    return res

@router.get(
    "/{id}/preview",
    response_model=DocumentPreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate temporary preview URL",
    response_description="Temporary secure signed preview URL"
)
async def preview(
    id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a secure, temporary (10-minute expiry) preview URL for a document.
    Accessible by owner or authorized share recipient.
    """
    res = await DocumentAccessService.generate_preview_url(
        db=db,
        document_id=id,
        requesting_user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    return DocumentPreviewResponse(success=True, data=res)

@router.get(
    "/{id}/download",
    response_model=DocumentDownloadResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate temporary download URL",
    response_description="Temporary secure signed download URL"
)
async def download(
    id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a secure, temporary (15-minute expiry) download URL for a document.
    Accessible by owner or authorized share recipient with download permission.
    """
    res = await DocumentAccessService.generate_download_url(
        db=db,
        document_id=id,
        requesting_user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    return DocumentDownloadResponse(success=True, data=res)

@router.put(
    "/{id}",
    response_model=DocumentDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update document metadata",
    response_description="Updated document metadata"
)
async def update(
    id: uuid.UUID,
    update_data: DocumentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update details (title, description, document_type, expiry_date) of an existing document.
    """
    doc = await update_document(
        db=db,
        doc_id=id,
        user_id=current_user.id,
        update_data=update_data
    )
    return DocumentDetailResponse.model_validate(doc)

@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a document",
    response_description="Deletion success confirmation"
)
async def delete(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a document from both PostgreSQL metadata and Supabase Storage.
    """
    await delete_document(db=db, doc_id=id, user_id=current_user.id)
    return {"message": "Document deleted successfully"}
