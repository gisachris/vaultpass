import uuid
import re
import logging
from typing import Tuple, List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.models.trusted_contact import TrustedContact
from vaultpass_backend.models.user import User
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
        Automatically links to an existing VaultPass account if the email matches.
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

        # Auto-link to a registered VaultPass user by email match (case-insensitive)
        user_result = await db.execute(
            select(User).where(func.lower(User.email) == contact_data.email.lower())
        )
        matched_user = user_result.scalar_one_or_none()
        linked_user_id = matched_user.id if matched_user else None

        # Resolve the contact's display name: prefer an explicitly provided
        # name, otherwise the matched registered user's real name, otherwise
        # a placeholder derived from the email (overwritten with the real
        # name once the invitee registers — see reconcile_new_user_contacts).
        if contact_data.full_name and contact_data.full_name.strip():
            resolved_full_name = contact_data.full_name.strip()
        elif matched_user:
            resolved_full_name = matched_user.full_name
        else:
            resolved_full_name = TrustedContactService._derive_name_from_email(contact_data.email)

        contact = TrustedContact(
            owner_id=owner_id,
            full_name=resolved_full_name,
            email=contact_data.email,
            phone_number=contact_data.phone_number,
            relationship=contact_data.relationship,
            notes=contact_data.notes,
            linked_user_id=linked_user_id,
        )

        created_contact = await TrustedContactRepository.create_contact(db, contact)
        logger.info(f"User {owner_id} created trusted contact {created_contact.id} (linked_user_id={linked_user_id})")

        # Trigger notification event (owner side — unchanged)
        from vaultpass_backend.services.notification import NotificationService
        await NotificationService.notify_contact_added(db, owner_id, created_contact.id, created_contact.full_name)

        # Notify the linked contact themselves, if they are a registered user
        if linked_user_id:
            owner_result = await db.execute(select(User).where(User.id == owner_id))
            owner = owner_result.scalar_one_or_none()
            owner_name = owner.full_name if owner else "Someone"
            await NotificationService.notify_added_as_trusted_contact(
                db=db,
                user_id=linked_user_id,
                owner_name=owner_name,
                contact_id=created_contact.id,
            )

        # Audit log
        from vaultpass_backend.services.audit_service import AuditService
        from vaultpass_backend.core import constants
        await AuditService.log_action(
            db=db,
            user_id=owner_id,
            action=constants.CONTACT_CREATED,
            entity_type="TRUSTED_CONTACT",
            entity_id=created_contact.id,
            description=f"Trusted contact '{created_contact.full_name}' created.",
        )

        return created_contact

    @staticmethod
    def _derive_name_from_email(email: str) -> str:
        """
        Best-effort placeholder display name derived from an email's local
        part, used when no name was provided and the email doesn't match a
        registered user yet. Replaced with the invitee's real name once they
        register (see reconcile_new_user_contacts).
        """
        local_part = email.split("@", 1)[0]
        words = [w for w in re.split(r"[._+\-]+", local_part) if w]
        if not words:
            return email
        return " ".join(word.capitalize() for word in words)

    @staticmethod
    async def reconcile_new_user_contacts(db: AsyncSession, new_user: User) -> None:
        """
        Called immediately after a brand-new user registers. Finds every
        pre-existing trusted_contacts row (across ALL owners) whose email
        matches the new user's email case-insensitively and is not yet
        linked to any user, links it to the new account, and notifies the
        new user for each match.
        """
        matches = await TrustedContactRepository.get_unlinked_contacts_by_email(db, new_user.email)
        if not matches:
            return

        from vaultpass_backend.services.notification import NotificationService
        from vaultpass_backend.services.audit_service import AuditService
        from vaultpass_backend.core import constants

        for contact in matches:
            await TrustedContactRepository.update_contact(
                db, contact, {"linked_user_id": new_user.id, "full_name": new_user.full_name}
            )
            owner_name = contact.owner.full_name if contact.owner else "Someone"

            await NotificationService.notify_added_as_trusted_contact(
                db=db,
                user_id=new_user.id,
                owner_name=owner_name,
                contact_id=contact.id,
            )

            await AuditService.log_action(
                db=db,
                user_id=new_user.id,
                action=constants.CONTACT_LINKED_TO_USER,
                entity_type="TRUSTED_CONTACT",
                entity_id=contact.id,
                description=f"Newly registered account linked to existing trusted-contact entry owned by '{owner_name}'.",
            )

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

        # If email is being updated, verify no conflict and re-evaluate the linked user
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
            # Re-link (or unlink) based on the new email (case-insensitive)
            user_result = await db.execute(
                select(User).where(func.lower(User.email) == new_email.lower())
            )
            matched_user = user_result.scalar_one_or_none()
            update_dict["linked_user_id"] = matched_user.id if matched_user else None

        updated_contact = await TrustedContactRepository.update_contact(db, contact, update_dict)
        logger.info(f"User {user_id} updated trusted contact {contact_id}")

        # Trigger notification event
        from vaultpass_backend.services.notification import NotificationService
        await NotificationService.notify_contact_updated(db, user_id, updated_contact.id, updated_contact.full_name)

        # Audit log
        from vaultpass_backend.services.audit_service import AuditService
        from vaultpass_backend.core import constants
        await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=constants.CONTACT_UPDATED,
            entity_type="TRUSTED_CONTACT",
            entity_id=updated_contact.id,
            description=f"Trusted contact '{updated_contact.full_name}' updated.",
        )

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

        # Audit log
        from vaultpass_backend.services.audit_service import AuditService
        from vaultpass_backend.core import constants
        await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=constants.CONTACT_DELETED,
            entity_type="TRUSTED_CONTACT",
            entity_id=contact_id,
            description=f"Trusted contact '{contact_name}' deleted.",
        )

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
