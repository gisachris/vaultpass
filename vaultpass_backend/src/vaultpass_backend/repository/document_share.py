import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from vaultpass_backend.models.document_share import DocumentShare

class DocumentShareRepository:
    """
    Repository class encapsulating database operations for Document Shares.
    Contains database logic only. No business logic.
    """

    @staticmethod
    async def create_share(db: AsyncSession, share: DocumentShare) -> DocumentShare:
        """
        Add a new document share to the database.
        """
        db.add(share)
        await db.commit()
        await db.refresh(share)
        return share

    @staticmethod
    async def get_share_by_id(db: AsyncSession, share_id: uuid.UUID) -> Optional[DocumentShare]:
        """
        Retrieve a document share by its UUID.
        """
        query = select(DocumentShare).where(DocumentShare.id == share_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_share_by_token(db: AsyncSession, token: str) -> Optional[DocumentShare]:
        """
        Retrieve a document share by access token, preloading the associated document.
        """
        query = (
            select(DocumentShare)
            .where(DocumentShare.access_token == token)
            .options(selectinload(DocumentShare.document))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_shares(db: AsyncSession, owner_id: uuid.UUID) -> List[DocumentShare]:
        """
        Retrieve all document shares owned by a specific user.
        Ordered by created_at descending.
        """
        query = (
            select(DocumentShare)
            .where(DocumentShare.owner_id == owner_id)
            .order_by(DocumentShare.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_document_shares(
        db: AsyncSession,
        document_id: uuid.UUID,
        owner_id: uuid.UUID
    ) -> List[DocumentShare]:
        """
        Retrieve all shares associated with a specific document owned by the user.
        Ordered by created_at descending.
        """
        query = (
            select(DocumentShare)
            .where(
                DocumentShare.document_id == document_id,
                DocumentShare.owner_id == owner_id
            )
            .order_by(DocumentShare.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_share(
        db: AsyncSession,
        share: DocumentShare,
        update_dict: dict
    ) -> DocumentShare:
        """
        Update fields on a document share instance and commit.
        """
        for key, value in update_dict.items():
            setattr(share, key, value)
        await db.commit()
        await db.refresh(share)
        return share

    @staticmethod
    async def delete_share(db: AsyncSession, share: DocumentShare) -> None:
        """
        Delete a document share permanently from the database.
        """
        await db.delete(share)
        await db.commit()

    @staticmethod
    async def revoke_share(db: AsyncSession, share: DocumentShare) -> DocumentShare:
        """
        Set a document share to inactive.
        """
        share.is_active = False
        await db.commit()
        await db.refresh(share)
        return share

    @staticmethod
    async def activate_share(db: AsyncSession, share: DocumentShare) -> DocumentShare:
        """
        Set a document share to active.
        """
        share.is_active = True
        await db.commit()
        await db.refresh(share)
        return share

    @staticmethod
    async def get_received_shares(
        db: AsyncSession, recipient_user_id: uuid.UUID
    ) -> List[DocumentShare]:
        """
        Retrieve all active document shares where the authenticated user is
        the designated recipient. Preloads document and owner for response mapping.
        Ordered newest-first.
        """
        query = (
            select(DocumentShare)
            .where(DocumentShare.recipient_user_id == recipient_user_id)
            .options(
                selectinload(DocumentShare.document),
                selectinload(DocumentShare.owner),
            )
            .order_by(DocumentShare.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_received_share_by_id(
        db: AsyncSession, share_id: uuid.UUID, recipient_user_id: uuid.UUID
    ) -> Optional[DocumentShare]:
        """
        Retrieve a single received share by ID, verifying the recipient matches.
        Preloads document and owner.
        """
        query = (
            select(DocumentShare)
            .where(
                DocumentShare.id == share_id,
                DocumentShare.recipient_user_id == recipient_user_id,
            )
            .options(
                selectinload(DocumentShare.document),
                selectinload(DocumentShare.owner),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def count_received_shares(
        db: AsyncSession, recipient_user_id: uuid.UUID
    ) -> int:
        """
        Count all document shares received by the authenticated user.
        """
        from sqlalchemy import func
        query = (
            select(func.count())
            .select_from(DocumentShare)
            .where(DocumentShare.recipient_user_id == recipient_user_id)
        )
        result = await db.execute(query)
        return result.scalar() or 0
