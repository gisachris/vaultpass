import uuid
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from vaultpass_backend.models.trusted_contact import TrustedContact

class TrustedContactRepository:
    """
    Repository class encapsulating raw database transactions for Trusted Contacts.
    Contains database logic only. No business logic.
    """

    @staticmethod
    async def create_contact(db: AsyncSession, contact: TrustedContact) -> TrustedContact:
        """
        Add a new trusted contact to the database.
        """
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact

    @staticmethod
    async def get_contact_by_id(db: AsyncSession, contact_id: uuid.UUID) -> Optional[TrustedContact]:
        """
        Retrieve a trusted contact by its UUID.
        """
        query = select(TrustedContact).where(TrustedContact.id == contact_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_contact_by_email(db: AsyncSession, email: str, owner_id: uuid.UUID) -> Optional[TrustedContact]:
        """
        Retrieve a trusted contact by email and owner ID.
        Used to enforce uniqueness per owner.
        """
        query = select(TrustedContact).where(
            TrustedContact.owner_id == owner_id,
            TrustedContact.email == email
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_contacts(
        db: AsyncSession,
        owner_id: uuid.UUID,
        offset: int,
        limit: int
    ) -> List[TrustedContact]:
        """
        Retrieve a paginated list of trusted contacts belonging to a user.
        Ordered by created_at descending.
        """
        query = (
            select(TrustedContact)
            .where(TrustedContact.owner_id == owner_id)
            .order_by(TrustedContact.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_contact(
        db: AsyncSession,
        contact: TrustedContact,
        update_dict: dict
    ) -> TrustedContact:
        """
        Update fields on a trusted contact instance and save to the database.
        """
        for key, value in update_dict.items():
            setattr(contact, key, value)
        await db.commit()
        await db.refresh(contact)
        return contact

    @staticmethod
    async def delete_contact(db: AsyncSession, contact: TrustedContact) -> None:
        """
        Delete a trusted contact from the database.
        """
        await db.delete(contact)
        await db.commit()

    @staticmethod
    async def search_contacts(
        db: AsyncSession,
        owner_id: uuid.UUID,
        search_query: str,
        offset: int,
        limit: int
    ) -> List[TrustedContact]:
        """
        Search user's trusted contacts matching full_name, email, or relationship (case-insensitive).
        Ordered by created_at descending.
        """
        search_pattern = f"%{search_query}%"
        query = (
            select(TrustedContact)
            .where(
                TrustedContact.owner_id == owner_id,
                (
                    TrustedContact.full_name.ilike(search_pattern) |
                    TrustedContact.email.ilike(search_pattern) |
                    TrustedContact.relationship.ilike(search_pattern)
                )
            )
            .order_by(TrustedContact.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def count_contacts(
        db: AsyncSession,
        owner_id: uuid.UUID,
        search_query: Optional[str] = None
    ) -> int:
        """
        Get the total count of contacts owned by the user, with optional search filtering.
        """
        query = select(func.count()).select_from(TrustedContact).where(TrustedContact.owner_id == owner_id)
        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.where(
                TrustedContact.full_name.ilike(search_pattern) |
                TrustedContact.email.ilike(search_pattern) |
                TrustedContact.relationship.ilike(search_pattern)
            )
        result = await db.execute(query)
        return result.scalar_one()
