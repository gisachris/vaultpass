import uuid
from datetime import datetime
from typing import Optional, Tuple, List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.models.document import Document, DocumentType
from vaultpass_backend.models.user import User
from vaultpass_backend.schemas.document import DocumentUpdateRequest
from vaultpass_backend.services.supabase_storage import storage_service

# Constants for validation
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/jpg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_file(file: UploadFile) -> int:
    """
    Validate file extension, mime type, and size.
    Returns the file size in bytes.
    """
    # 1. Check extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File has no name"
        )
    
    filename = file.filename.lower()
    has_valid_ext = any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS)
    if not has_valid_ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Allowed: PDF, PNG, JPG, JPEG"
        )

    # 2. Check mime type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: PDF, PNG, JPG, JPEG"
        )

    # 3. Check file size
    try:
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not determine file size"
        )

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum limit of 10MB"
        )
    
    return file_size

async def upload_document(
    db: AsyncSession,
    owner_id: uuid.UUID,
    file: UploadFile,
    title: str,
    document_type: DocumentType,
    description: Optional[str] = None,
    expiry_date: Optional[datetime] = None,
    guardian_visibility: bool = True
) -> Document:
    """
    Upload file to storage, insert metadata to database, and return the document.
    """
    # Validate file
    file_size = await validate_file(file)
    
    # Generate a unique path: owner_id/uuid_filename
    unique_id = uuid.uuid4()
    # Clean the file name to prevent path traversal or other issues
    filename = file.filename or "file"
    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    file_path = f"{owner_id}/{unique_id}_{safe_filename}"
    
    # Upload to Supabase Storage
    await storage_service.upload_file(file_path, file)
    
    # Create database record
    new_doc = Document(
        id=unique_id,
        owner_id=owner_id,
        title=title,
        document_type=document_type,
        description=description,
        file_name=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        expiry_date=expiry_date,
        guardian_visibility=guardian_visibility
    )
    
    try:
        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)
        
        # Trigger notification event
        from vaultpass_backend.services.notification import NotificationService
        await NotificationService.notify_document_uploaded(db, owner_id, new_doc.id, new_doc.title)

        # Audit log
        from vaultpass_backend.services.audit_service import AuditService
        from vaultpass_backend.core import constants
        await AuditService.log_action(
            db=db,
            user_id=owner_id,
            action=constants.DOCUMENT_CREATED,
            entity_type="DOCUMENT",
            entity_id=new_doc.id,
            description=f"Document '{new_doc.title}' uploaded.",
        )

        return new_doc
    except Exception as e:
        # Rollback database transaction and attempt cleanup from Supabase Storage
        await db.rollback()
        try:
            await storage_service.delete_file(file_path)
        except Exception:
            pass  # Avoid masking the original database error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database transaction failed: {str(e)}"
        )

async def get_document_by_id(
    db: AsyncSession,
    doc_id: uuid.UUID,
    user_id: uuid.UUID,
    allow_guardian: bool = False
) -> Document:
    """
    Retrieve document by id, raising 404 if not found and 403 if user is not the owner (or guardian if allowed).
    """
    query = select(Document).where(Document.id == doc_id)
    result = await db.execute(query)
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    if doc.owner_id != user_id:
        if allow_guardian and doc.guardian_visibility:
            from vaultpass_backend.repository.family import FamilyRepository
            is_guardian = await FamilyRepository.check_is_guardian(db, guardian_id=user_id, dependent_id=doc.owner_id)
            if is_guardian:
                return doc
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this document"
        )
        
    return doc

async def get_documents(
    db: AsyncSession,
    user_id: uuid.UUID,
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None
) -> Tuple[List[Document], int]:
    """
    Retrieve user's documents with pagination and optional search filter.
    Returns (items, total_count).
    """
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10
    
    offset = (page - 1) * limit
    
    # Construct queries
    count_query = select(func.count()).select_from(Document).where(Document.owner_id == user_id)
    items_query = select(Document).where(Document.owner_id == user_id)
    
    if search:
        search_filter = Document.title.ilike(f"%{search}%")
        count_query = count_query.where(search_filter)
        items_query = items_query.where(search_filter)
        
    # Execute count
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    
    # Execute query with offset & limit
    items_query = items_query.order_by(Document.created_at.desc()).offset(offset).limit(limit)
    items_result = await db.execute(items_query)
    items = list(items_result.scalars().all())
    
    return items, total

async def generate_download_link(
    db: AsyncSession,
    doc_id: uuid.UUID,
    user_id: uuid.UUID
) -> str:
    """
    Generate a secure temporary download URL for a document.
    """
    doc = await get_document_by_id(db, doc_id, user_id)
    # Generate 1-hour secure URL
    signed_url = await storage_service.generate_signed_url(doc.file_path, expires_in_seconds=3600)

    # Audit log
    from vaultpass_backend.services.audit_service import AuditService
    from vaultpass_backend.core import constants
    await AuditService.log_action(
        db=db,
        user_id=user_id,
        action=constants.DOCUMENT_DOWNLOADED,
        entity_type="DOCUMENT",
        entity_id=doc_id,
        description=f"Download link generated for document '{doc.title}'.",
    )

    return signed_url

async def update_document(
    db: AsyncSession,
    doc_id: uuid.UUID,
    user_id: uuid.UUID,
    update_data: DocumentUpdateRequest
) -> Document:
    """
    Update document metadata.
    """
    doc = await get_document_by_id(db, doc_id, user_id)
    
    # Update only provided fields
    if update_data.title is not None:
        doc.title = update_data.title
    if update_data.description is not None:
        doc.description = update_data.description
    if update_data.expiry_date is not None:
        doc.expiry_date = update_data.expiry_date
    if update_data.document_type is not None:
        doc.document_type = update_data.document_type
    if update_data.guardian_visibility is not None:
        if doc.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify guardian visibility"
            )
        old_vis = doc.guardian_visibility
        doc.guardian_visibility = update_data.guardian_visibility
        if old_vis != update_data.guardian_visibility:
            from vaultpass_backend.core import constants
            from vaultpass_backend.services.audit_service import AuditService
            action = constants.DOCUMENT_VISIBILITY_ENABLED if update_data.guardian_visibility else constants.DOCUMENT_VISIBILITY_DISABLED
            desc = f"Guardian visibility enabled for document '{doc.title}'." if update_data.guardian_visibility else f"Guardian visibility disabled for document '{doc.title}'."
            await AuditService.log_action(
                db=db,
                user_id=user_id,
                action=action,
                entity_type="DOCUMENT",
                entity_id=doc.id,
                description=desc
            )
        
    await db.commit()
    await db.refresh(doc)
    
    # Trigger notification event
    from vaultpass_backend.services.notification import NotificationService
    await NotificationService.notify_document_updated(db, user_id, doc.id, doc.title)

    # Audit log
    from vaultpass_backend.services.audit_service import AuditService
    from vaultpass_backend.core import constants
    await AuditService.log_action(
        db=db,
        user_id=user_id,
        action=constants.DOCUMENT_UPDATED,
        entity_type="DOCUMENT",
        entity_id=doc.id,
        description=f"Document '{doc.title}' metadata updated.",
    )

    return doc

async def delete_document(
    db: AsyncSession,
    doc_id: uuid.UUID,
    user_id: uuid.UUID
) -> None:
    """
    Delete document metadata from DB and file from storage.
    """
    doc = await get_document_by_id(db, doc_id, user_id)
    
    # Delete from Supabase Storage first
    await storage_service.delete_file(doc.file_path)
    
    doc_title = doc.title
    doc_id = doc.id

    # Delete from DB
    await db.delete(doc)
    await db.commit()

    # Trigger notification event
    from vaultpass_backend.services.notification import NotificationService
    await NotificationService.notify_document_deleted(db, user_id, doc_title)

    # Audit log
    from vaultpass_backend.services.audit_service import AuditService
    from vaultpass_backend.core import constants
    await AuditService.log_action(
        db=db,
        user_id=user_id,
        action=constants.DOCUMENT_DELETED,
        entity_type="DOCUMENT",
        entity_id=doc_id,
        description=f"Document '{doc_title}' deleted.",
    )
