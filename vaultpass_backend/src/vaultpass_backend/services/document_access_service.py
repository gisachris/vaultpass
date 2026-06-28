import uuid
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from vaultpass_backend.models.document import Document
from vaultpass_backend.models.document_share import DocumentShare
from vaultpass_backend.models.user import User
from vaultpass_backend.services.supabase_storage import storage_service
from vaultpass_backend.services.notification import NotificationService
from vaultpass_backend.services.audit_service import AuditService
from vaultpass_backend.core import constants

class DocumentAccessService:
    """
    Service to handle resolving permission-aware access for previews and downloads,
    generating signed storage URLs, audit logging, and owner notifications.
    """

    @staticmethod
    async def resolve_document_access(
        db: AsyncSession,
        document_id: uuid.UUID,
        requesting_user_id: uuid.UUID
    ) -> Tuple[Document, Optional[DocumentShare]]:
        """
        Verify if requesting_user_id has access to document_id.
        Access is granted if:
          1. requesting_user_id is the owner of the document.
          2. requesting_user_id is the recipient of an active, non-expired internal document share.

        Returns:
          Tuple[Document, Optional[DocumentShare]]: The document and the active share (None if owner).
        """
        # Fetch document
        doc_query = select(Document).where(Document.id == document_id)
        doc_res = await db.execute(doc_query)
        doc = doc_res.scalar_one_or_none()

        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # 1. Owner check
        if doc.owner_id == requesting_user_id:
            return doc, None

        # 2. Guardian check (before document sharing check)
        from vaultpass_backend.repository.family import FamilyRepository
        is_guardian = await FamilyRepository.check_is_guardian(db, guardian_id=requesting_user_id, dependent_id=doc.owner_id)
        if is_guardian:
            return doc, None

        # 3. Share check
        share_query = select(DocumentShare).where(
            DocumentShare.document_id == document_id,
            DocumentShare.recipient_user_id == requesting_user_id,
            DocumentShare.is_active == True
        )
        share_res = await db.execute(share_query)
        share = share_res.scalar_one_or_none()

        if not share:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this document"
            )

        # Expiry check
        if share.expires_at:
            expires_at = share.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail="Share link has expired"
                )

        return doc, share

    @staticmethod
    async def generate_preview_url(
        db: AsyncSession,
        document_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> dict:
        """
        Resolve access, generate a short-lived preview signed URL,
        write audit log, and notify the owner if accessed via a share.
        """
        doc, share = await DocumentAccessService.resolve_document_access(db, document_id, requesting_user_id)

        # Preview expires in 10 minutes (600 seconds)
        expires_in = 600
        preview_url = await storage_service.generate_signed_url(doc.file_path, expires_in)
        expires_at_dt = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Check if guardian access
        is_guardian_access = (doc.owner_id != requesting_user_id) and (share is None)
        action = constants.GUARDIAN_DOCUMENT_ACCESSED if is_guardian_access else constants.DOCUMENT_PREVIEWED

        # Audit Log
        await AuditService.log_action(
            db=db,
            user_id=requesting_user_id,
            action=action,
            entity_type="DOCUMENT",
            entity_id=doc.id,
            description=f"Accessed document '{doc.title}' via guardian relationship" if is_guardian_access else f"Previewed document '{doc.title}'",
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Notify Owner if recipient accessed it
        if share:
            # Get viewer's full name
            viewer_query = select(User).where(User.id == requesting_user_id)
            viewer_res = await db.execute(viewer_query)
            viewer = viewer_res.scalar_one_or_none()
            viewer_name = viewer.full_name if viewer else "Someone"

            await NotificationService.notify_document_previewed_by_recipient(
                db=db,
                owner_id=doc.owner_id,
                viewer_name=viewer_name,
                doc_title=doc.title,
                doc_id=doc.id,
                share_id=share.id
            )

        return {
            "document_id": doc.id,
            "file_name": doc.file_name,
            "file_type": doc.mime_type,
            "preview_url": preview_url,
            "expires_at": expires_at_dt.isoformat()
        }

    @staticmethod
    async def generate_download_url(
        db: AsyncSession,
        document_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> dict:
        """
        Resolve access, enforce allow_download check for shares, generate a short-lived download signed URL,
        write audit log, and notify the owner if accessed via a share.
        """
        doc, share = await DocumentAccessService.resolve_document_access(db, document_id, requesting_user_id)

        # If accessed via share, allow_download must be True
        if share and not share.allow_download:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Download is not allowed for this share"
            )

        # Download expires in 15 minutes (900 seconds)
        expires_in = 900
        download_url = await storage_service.generate_signed_url(doc.file_path, expires_in)
        expires_at_dt = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Check if guardian access
        is_guardian_access = (doc.owner_id != requesting_user_id) and (share is None)
        action = constants.GUARDIAN_DOCUMENT_ACCESSED if is_guardian_access else constants.DOCUMENT_DOWNLOADED

        # Audit Log
        await AuditService.log_action(
            db=db,
            user_id=requesting_user_id,
            action=action,
            entity_type="DOCUMENT",
            entity_id=doc.id,
            description=f"Accessed document '{doc.title}' via guardian relationship" if is_guardian_access else f"Downloaded document '{doc.title}'",
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Notify Owner if recipient accessed it
        if share:
            downloader_query = select(User).where(User.id == requesting_user_id)
            downloader_res = await db.execute(downloader_query)
            downloader = downloader_res.scalar_one_or_none()
            downloader_name = downloader.full_name if downloader else "Someone"

            await NotificationService.notify_document_downloaded_by_recipient(
                db=db,
                owner_id=doc.owner_id,
                downloader_name=downloader_name,
                doc_title=doc.title,
                doc_id=doc.id,
                share_id=share.id
            )

        return {
            "document_id": doc.id,
            "file_name": doc.file_name,
            "download_url": download_url,
            "expires_at": expires_at_dt.isoformat()
        }
