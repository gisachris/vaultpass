import uuid
import secrets
from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from vaultpass_backend.models.document_share import DocumentShare
from vaultpass_backend.models.document import Document
from vaultpass_backend.models.trusted_contact import TrustedContact
from vaultpass_backend.repository.document_share import DocumentShareRepository
from vaultpass_backend.schemas.document_share import (
    CreateDocumentShareRequest,
    UpdateDocumentShareRequest,
    SharedWithMeResponse,
    SharedWithMeDetailResponse,
)
from vaultpass_backend.services.supabase_storage import storage_service

class DocumentShareService:
    """
    Service layer containing all business logic, validations, and ownership enforcement for Document Shares.
    """

    @staticmethod
    async def create_share(
        db: AsyncSession,
        owner_id: uuid.UUID,
        share_data: CreateDocumentShareRequest
    ) -> DocumentShare:
        """
        Create a new document share.
        Validates document ownership and trusted contact ownership.
        """
        # Validate document existence and ownership
        doc_query = select(Document).where(Document.id == share_data.document_id)
        doc_res = await db.execute(doc_query)
        doc = doc_res.scalar_one_or_none()

        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        if doc.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this document"
            )

        # Validate trusted contact existence and ownership
        contact_query = select(TrustedContact).where(TrustedContact.id == share_data.contact_id)
        contact_res = await db.execute(contact_query)
        contact = contact_res.scalar_one_or_none()

        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trusted contact not found"
            )
        if contact.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this trusted contact"
            )

        # Generate a secure access token (used for external shares; stored for all)
        access_token = secrets.token_urlsafe(48)

        from vaultpass_backend.core.security import get_password_hash
        password_hash = get_password_hash(share_data.password) if getattr(share_data, 'password', None) else None

        new_share = DocumentShare(
            document_id=share_data.document_id,
            contact_id=share_data.contact_id,
            owner_id=owner_id,
            access_token=access_token,
            expires_at=share_data.expires_at,
            is_active=True,
            recipient_user_id=contact.linked_user_id,  # None for external shares
            access_level=getattr(share_data, 'access_level', None),
            allow_download=getattr(share_data, 'allow_download', True),
            password_hash=password_hash,
        )

        saved_share = await DocumentShareRepository.create_share(db, new_share)

        from vaultpass_backend.services.notification import NotificationService
        from vaultpass_backend.services.audit_service import AuditService
        from vaultpass_backend.core import constants

        if contact.linked_user_id:
            # ── INTERNAL SHARE: recipient is a registered VaultPass user ──────
            # Fetch owner's name for the notification message
            from vaultpass_backend.models.user import User
            owner_result = await db.execute(select(User).where(User.id == owner_id))
            owner = owner_result.scalar_one_or_none()
            owner_name = owner.full_name if owner else "Someone"

            await NotificationService.notify_internal_share_received(
                db=db,
                recipient_user_id=contact.linked_user_id,
                owner_name=owner_name,
                doc_title=doc.title,
                share_id=saved_share.id,
                doc_id=doc.id,
                contact_id=contact.id,
            )
            await AuditService.log_action(
                db=db,
                user_id=owner_id,
                action=constants.DOCUMENT_SHARED_INTERNAL,
                entity_type="DOCUMENT_SHARE",
                entity_id=saved_share.id,
                description=f"Document '{doc.title}' shared internally with '{contact.full_name}' (VaultPass user).",
            )
        else:
            # ── EXTERNAL SHARE: recipient is not a VaultPass user ─────────────
            await NotificationService.notify_document_shared(
                db=db,
                owner_id=owner_id,
                share_id=saved_share.id,
                doc_title=doc.title,
                contact_name=contact.full_name,
                doc_id=doc.id,
                contact_id=contact.id,
            )
            await AuditService.log_action(
                db=db,
                user_id=owner_id,
                action=constants.DOCUMENT_SHARED_EXTERNAL,
                entity_type="DOCUMENT_SHARE",
                entity_id=saved_share.id,
                description=f"Document '{doc.title}' shared externally with '{contact.full_name}'.",
            )

        return saved_share

    @staticmethod
    async def get_share_by_id(
        db: AsyncSession,
        share_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> DocumentShare:
        """
        Retrieve a share details by ID. Enforces ownership.
        """
        share = await DocumentShareRepository.get_share_by_id(db, share_id)
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document share not found"
            )
        if share.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this document share"
            )
        return share

    @staticmethod
    async def get_my_shares(db: AsyncSession, user_id: uuid.UUID) -> List[DocumentShare]:
        """
        Retrieve all document shares generated by the user.
        """
        return await DocumentShareRepository.get_user_shares(db, user_id)

    @staticmethod
    async def get_shares_for_document(
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> List[DocumentShare]:
        """
        Retrieve all shares generated for a document. Enforces document ownership.
        """
        doc_query = select(Document).where(Document.id == document_id)
        doc_res = await db.execute(doc_query)
        doc = doc_res.scalar_one_or_none()

        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        if doc.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this document"
            )

        return await DocumentShareRepository.get_document_shares(db, document_id, user_id)

    @staticmethod
    async def update_share(
        db: AsyncSession,
        share_id: uuid.UUID,
        user_id: uuid.UUID,
        update_data: UpdateDocumentShareRequest
    ) -> DocumentShare:
        """
        Update share link configuration. Enforces ownership.
        """
        share = await DocumentShareService.get_share_by_id(db, share_id, user_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return share

        return await DocumentShareRepository.update_share(db, share, update_dict)

    @staticmethod
    async def revoke_share(
        db: AsyncSession,
        share_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> DocumentShare:
        """
        Deactivate a share link. Enforces ownership.
        """
        share = await DocumentShareService.get_share_by_id(db, share_id, user_id)
        revoked_share = await DocumentShareRepository.revoke_share(db, share)

        # Fetch document title for notification
        doc_query = select(Document.title).where(Document.id == share.document_id)
        doc_res = await db.execute(doc_query)
        doc_title = doc_res.scalar() or "document"

        # Trigger notification event
        from vaultpass_backend.services.notification import NotificationService
        await NotificationService.notify_share_revoked(
            db=db,
            owner_id=user_id,
            share_id=share_id,
            doc_title=doc_title,
            doc_id=share.document_id,
            contact_id=share.contact_id
        )

        # Audit log
        from vaultpass_backend.services.audit_service import AuditService
        from vaultpass_backend.core import constants
        await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=constants.SHARE_REVOKED,
            entity_type="DOCUMENT_SHARE",
            entity_id=share_id,
            description=f"Share access revoked for document '{doc_title}'.",
        )

        return revoked_share

    @staticmethod
    async def activate_share(
        db: AsyncSession,
        share_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> DocumentShare:
        """
        Reactivate a share link. Enforces ownership.
        """
        share = await DocumentShareService.get_share_by_id(db, share_id, user_id)
        return await DocumentShareRepository.activate_share(db, share)

    @staticmethod
    async def delete_share(
        db: AsyncSession,
        share_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> None:
        """
        Permanently delete a share link. Enforces ownership.
        """
        share = await DocumentShareService.get_share_by_id(db, share_id, user_id)
        await DocumentShareRepository.delete_share(db, share)

    @staticmethod
    async def get_public_share_by_token(db: AsyncSession, token: str, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate token public link and return document metadata with temporary secure download URL.
        No authentication required.
        Updates last_accessed_at timestamp.
        """
        share = await DocumentShareRepository.get_share_by_token(db, token)
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid share link or token"
            )

        if not share.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This share link has been deactivated"
            )

        if share.expires_at and share.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This share link has expired"
            )

        # Check password protection if password_hash exists
        if share.password_hash:
            if not password:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="password_required"
                )
            from vaultpass_backend.core.security import verify_password
            if not verify_password(password, share.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="incorrect_password"
                )

        # Check if the underlying document still exists in the database
        if not share.document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shared document no longer exists"
            )

        # Update last_accessed_at timestamp
        await DocumentShareRepository.update_share(db, share, {"last_accessed_at": datetime.now(timezone.utc)})

        # Fetch contact name for notification
        contact_query = select(TrustedContact.full_name).where(TrustedContact.id == share.contact_id)
        contact_res = await db.execute(contact_query)
        contact_name = contact_res.scalar() or "A trusted contact"

        # Trigger notification event
        from vaultpass_backend.services.notification import NotificationService
        await NotificationService.notify_share_accessed(
            db=db,
            owner_id=share.owner_id,
            share_id=share.id,
            doc_title=share.document.title,
            contact_name=contact_name,
            doc_id=share.document_id
        )

        # Generate a temporary download link (1 hour) using Supabase Storage if allowed
        download_url = None
        if share.allow_download:
            download_url = await storage_service.generate_signed_url(share.document.file_path, expires_in_seconds=3600)

        # Return only the allowed non-private document metadata
        return {
            "title": share.document.title,
            "document_type": share.document.document_type,
            "created_at": share.document.created_at,
            "expiry_date": share.document.expiry_date,
            "download_url": download_url,
            "password_required": False,
            "allow_download": share.allow_download
        }

    @staticmethod
    async def get_shared_with_me(
        db: AsyncSession,
        recipient_user_id: uuid.UUID,
    ) -> List[SharedWithMeResponse]:
        """
        Return all document shares where the current user is the recipient.
        """
        shares = await DocumentShareRepository.get_received_shares(db, recipient_user_id)
        result = []
        for s in shares:
            doc = s.document
            owner = s.owner
            result.append(
                SharedWithMeResponse(
                    share_id=s.id,
                    document_id=s.document_id,
                    document_title=doc.title if doc else "Unknown",
                    document_type=(
                        doc.document_type.value
                        if doc and hasattr(doc.document_type, "value")
                        else str(doc.document_type) if doc else "UNKNOWN"
                    ),
                    owner_name=owner.full_name if owner else "Unknown",
                    shared_at=s.created_at,
                    expires_at=s.expires_at,
                    is_active=s.is_active,
                )
            )
        return result

    @staticmethod
    async def get_shared_with_me_detail(
        db: AsyncSession,
        share_id: uuid.UUID,
        recipient_user_id: uuid.UUID,
    ) -> SharedWithMeDetailResponse:
        """
        Return a single received share detail.
        Verifies that the current user is the designated recipient.
        """
        share = await DocumentShareRepository.get_received_share_by_id(
            db, share_id, recipient_user_id
        )
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shared document not found or you are not the recipient",
            )

        doc = share.document
        owner = share.owner
        return SharedWithMeDetailResponse(
            share_id=share.id,
            document_id=share.document_id,
            document_title=doc.title if doc else "Unknown",
            document_type=(
                doc.document_type.value
                if doc and hasattr(doc.document_type, "value")
                else str(doc.document_type) if doc else "UNKNOWN"
            ),
            owner_name=owner.full_name if owner else "Unknown",
            owner_id=share.owner_id,
            contact_id=share.contact_id,
            shared_at=share.created_at,
            expires_at=share.expires_at,
            is_active=share.is_active,
            last_accessed_at=share.last_accessed_at,
        )
