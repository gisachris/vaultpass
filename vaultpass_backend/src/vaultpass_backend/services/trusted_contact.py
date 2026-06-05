import uuid
import logging
from typing import Tuple, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.models.trusted_contact import TrustedContact
from vaultpass_backend.repository.trusted_contact import TrustedContactRepository
from vaultpass_backend.schemas.trusted_contact import TrustedContactCreate, TrustedContactUpdate

logger = logging.getLogger("vaultpass")

class TrustedContactService:
    """
    Service layer containing all business rules, authorization, logging, and validations.
    """

    @staticmethod
    async def create_contact(
        db: AsyncSession,
        owner_id: uuid.UUID,
        contact_data: TrustedContactCreate
    ) -> TrustedContact:
        """
        Create a new trusted contact.
        Validates that email is unique for this owner.
        """
        # Check duplicate contacts for this owner
        existing = await TrustedContactRepository.get_contact_by_email(
            db=db,
            email=contact_data.email,
            owner_id=owner_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Trusted contact with this email already exists"
            )

        contact = TrustedContact(
            owner_id=owner_id,
            full_name=contact_data.full_name,
            email=contact_data.email,
            phone_number=contact_data.phone_number,
            relationship=contact_data.relationship,
            notes=contact_data.notes
        )

        created_contact = await TrustedContactRepository.create_contact(db, contact)
        logger.info(f"User {owner_id} created trusted contact {created_contact.id}")
        
        # Trigger notification event
        from vaultpass_backend.services.notification import NotificationService
        await NotificationService.notify_contact_added(db, owner_id, created_contact.id, created_contact.full_name)
        
        return created_contact

    @staticmethod
    async def get_contact_by_id(
        db: AsyncSession,
        contact_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> TrustedContact:
        """
        Retrieve a single contact.
        Verifies existence and ownership.
        """
        contact = await TrustedContactRepository.get_contact_by_id(db, contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trusted contact not found"
            )

        if contact.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this trusted contact"
            )

        return contact

    @staticmethod
    async def update_contact(
        db: AsyncSession,
        contact_id: uuid.UUID,
        user_id: uuid.UUID,
        update_data: TrustedContactUpdate
    ) -> TrustedContact:
        """
        Update a trusted contact.
        Verifies ownership and duplicate constraints.
        """
        # Fetch and verify ownership/existence
        contact = await TrustedContactService.get_contact_by_id(db, contact_id, user_id)

        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return contact

        # If email is being updated, verify it doesn't conflict with another contact owned by this user
        new_email = update_dict.get("email")
        if new_email and new_email != contact.email:
            existing = await TrustedContactRepository.get_contact_by_email(
                db=db,
                email=new_email,
                owner_id=user_id
            )
            if existing and existing.id != contact_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Trusted contact with this email already exists"
                )

        updated_contact = await TrustedContactRepository.update_contact(db, contact, update_dict)
        logger.info(f"User {user_id} updated trusted contact {contact_id}")
        
        # Trigger notification event
        from vaultpass_backend.services.notification import NotificationService
        await NotificationService.notify_contact_updated(db, user_id, updated_contact.id, updated_contact.full_name)
        
        return updated_contact

    @staticmethod
    async def delete_contact(
        db: AsyncSession,
        contact_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> None:
        """
        Delete a trusted contact.
        Verifies ownership.
        """
        contact = await TrustedContactService.get_contact_by_id(db, contact_id, user_id)
        contact_name = contact.full_name
        await TrustedContactRepository.delete_contact(db, contact)
        logger.info(f"User {user_id} deleted trusted contact {contact_id}")
        
        # Trigger notification event
        from vaultpass_backend.services.notification import NotificationService
        await NotificationService.notify_contact_deleted(db, user_id, contact_name)

    @staticmethod
    async def list_contacts(
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[TrustedContact], int]:
        """
        List contacts with pagination.
        """
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10

        offset = (page - 1) * page_size
        items = await TrustedContactRepository.get_user_contacts(db, user_id, offset, page_size)
        total = await TrustedContactRepository.count_contacts(db, user_id)
        return items, total

    @staticmethod
    async def search_contacts(
        db: AsyncSession,
        user_id: uuid.UUID,
        search_query: str,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[TrustedContact], int]:
        """
        Search contacts with pagination.
        """
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10

        offset = (page - 1) * page_size
        items = await TrustedContactRepository.search_contacts(db, user_id, search_query, offset, page_size)
        total = await TrustedContactRepository.count_contacts(db, user_id, search_query)
        return items, total
