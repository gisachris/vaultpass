import uuid
from datetime import datetime, timezone, date
from typing import List, Optional, Tuple, Dict
from fastapi import HTTPException, status
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.models.family_relationship import FamilyRelationship, RelationshipType, RelationshipStatus
from vaultpass_backend.models.user import User
from vaultpass_backend.models.document import Document, DocumentType
from vaultpass_backend.repository.family import FamilyRepository
from vaultpass_backend.services.notification import NotificationService
from vaultpass_backend.models.notification import NotificationType
from vaultpass_backend.services.audit_service import AuditService
from vaultpass_backend.core import constants
from vaultpass_backend.schemas.family import (
    FamilyInvitationCreate,
    FamilySummaryResponse,
    DependentDocumentsResponse
)
from vaultpass_backend.schemas.document import DocumentCreateResponse

class FamilyService:
    @staticmethod
    async def create_invitation(
        db: AsyncSession, sender_id: uuid.UUID, schema: FamilyInvitationCreate
    ) -> FamilyRelationship:
        # 1. Verify account exists
        recipient_query = select(User).where(User.email == schema.email)
        recipient_res = await db.execute(recipient_query)
        recipient = recipient_res.scalar_one_or_none()

        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invited account does not exist"
            )

        # 2. Prevent self invitations
        if recipient.id == sender_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot invite yourself"
            )

        # 3. Check for inactive, deleted, or blocked users
        if not recipient.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invited user account is inactive"
            )

        # 4. Prevent duplicate or circular guardianship relationships
        existing = await FamilyRepository.get_active_or_pending_between_users(db, sender_id, recipient.id)
        if existing:
            if existing.status == RelationshipStatus.ACCEPTED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An active relationship already exists between these users"
                )
            elif existing.status == RelationshipStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A pending family invitation already exists between these users"
                )

        # Create invitation (sender is the guardian, recipient is the dependent)
        new_relation = FamilyRelationship(
            guardian_id=sender_id,
            dependent_id=recipient.id,
            relationship=schema.relationship,
            status=RelationshipStatus.PENDING,
            invited_by=sender_id,
            notes=schema.notes
        )

        relation = await FamilyRepository.create_relationship(db, new_relation)

        # Trigger notification
        sender_query = select(User).where(User.id == sender_id)
        sender_res = await db.execute(sender_query)
        sender = sender_res.scalar_one()

        await NotificationService.create_notification(
            db=db,
            user_id=recipient.id,
            title="Family Invitation Received",
            message=f"{sender.full_name} invited you as a family member.",
            type=NotificationType.INFO
        )

        # Log audit action
        await AuditService.log_action(
            db=db,
            user_id=sender_id,
            action=constants.FAMILY_INVITATION_CREATED,
            entity_type="FAMILY_RELATIONSHIP",
            entity_id=relation.id,
            description=f"Family invitation sent to {recipient.full_name} ({recipient.email})",
        )

        return relation

    @staticmethod
    async def get_sent_invitations(db: AsyncSession, user_id: uuid.UUID) -> List[FamilyRelationship]:
        return await FamilyRepository.get_sent_invitations(db, user_id)

    @staticmethod
    async def get_received_invitations(db: AsyncSession, user_id: uuid.UUID) -> List[FamilyRelationship]:
        return await FamilyRepository.get_received_invitations(db, user_id)

    @staticmethod
    async def accept_invitation(db: AsyncSession, relationship_id: uuid.UUID, user_id: uuid.UUID) -> FamilyRelationship:
        relation = await FamilyRepository.get_relationship_by_id(db, relationship_id)
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )

        if relation.dependent_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only accept invitations sent to you"
            )

        if relation.status != RelationshipStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation is not in a pending state"
            )

        relation.status = RelationshipStatus.ACCEPTED
        relation.accepted_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(relation)

        # Trigger notification to guardian
        await NotificationService.create_notification(
            db=db,
            user_id=relation.guardian_id,
            title="Family Invitation Accepted",
            message=f"{relation.dependent.full_name} accepted your family invitation.",
            type=NotificationType.SUCCESS
        )

        # Log audit action
        await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=constants.FAMILY_INVITATION_ACCEPTED,
            entity_type="FAMILY_RELATIONSHIP",
            entity_id=relation.id,
            description=f"Accepted family invitation from {relation.guardian.full_name}",
        )

        return relation

    @staticmethod
    async def decline_invitation(db: AsyncSession, relationship_id: uuid.UUID, user_id: uuid.UUID) -> FamilyRelationship:
        relation = await FamilyRepository.get_relationship_by_id(db, relationship_id)
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )

        if relation.dependent_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only decline invitations sent to you"
            )

        if relation.status != RelationshipStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation is not in a pending state"
            )

        relation.status = RelationshipStatus.DECLINED
        await db.commit()
        await db.refresh(relation)

        # Trigger notification to guardian
        await NotificationService.create_notification(
            db=db,
            user_id=relation.guardian_id,
            title="Family Invitation Declined",
            message=f"{relation.dependent.full_name} declined your family invitation.",
            type=NotificationType.INFO
        )

        # Log audit action
        await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=constants.FAMILY_INVITATION_DECLINED,
            entity_type="FAMILY_RELATIONSHIP",
            entity_id=relation.id,
            description=f"Declined family invitation from {relation.guardian.full_name}",
        )

        return relation

    @staticmethod
    async def remove_relationship(db: AsyncSession, relationship_id: uuid.UUID, user_id: uuid.UUID) -> None:
        relation = await FamilyRepository.get_relationship_by_id(db, relationship_id)
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relationship not found"
            )

        if user_id not in [relation.guardian_id, relation.dependent_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to remove this relationship"
            )

        relation.status = RelationshipStatus.REMOVED
        await db.commit()

        # Trigger notification to the other party
        other_party_id = relation.dependent_id if user_id == relation.guardian_id else relation.guardian_id
        await NotificationService.create_notification(
            db=db,
            user_id=other_party_id,
            title="Family Relationship Removed",
            message="Your family relationship status has been changed to removed.",
            type=NotificationType.INFO
        )

        # Log audit action
        await AuditService.log_action(
            db=db,
            user_id=user_id,
            action=constants.GUARDIAN_RELATIONSHIP_REMOVED,
            entity_type="FAMILY_RELATIONSHIP",
            entity_id=relationship_id,
            description="Removed family relationship",
        )

    @staticmethod
    async def get_family_members(db: AsyncSession, user_id: uuid.UUID) -> List[FamilyRelationship]:
        return await FamilyRepository.get_family_members(db, user_id)

    @staticmethod
    async def get_family_summary(db: AsyncSession, user_id: uuid.UUID) -> FamilySummaryResponse:
        # Counts: family_members, guardian_count, dependent_count, accessible_documents, pending_invitations
        (
            family_members,
            guardian_count,
            dependent_count,
            pending_invitations,
            accessible_documents
        ) = await asyncio_gather_summary_counts(db, user_id)

        return FamilySummaryResponse(
            family_members=family_members,
            guardian_count=guardian_count,
            dependent_count=dependent_count,
            accessible_documents=accessible_documents,
            pending_invitations=pending_invitations
        )

    @staticmethod
    async def get_guardian_documents(
        db: AsyncSession,
        guardian_id: uuid.UUID,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        category: Optional[str] = None,
        dependent_name: Optional[str] = None,
        document_type: Optional[DocumentType] = None,
        date_uploaded: Optional[str] = None,
        relationship: Optional[RelationshipType] = None
    ) -> List[DependentDocumentsResponse]:
        # Formulate query to fetch documents where owner is dependent of guardian
        stmt = (
            select(Document, FamilyRelationship, User)
            .join(FamilyRelationship, FamilyRelationship.dependent_id == Document.owner_id)
            .join(User, User.id == Document.owner_id)
            .where(
                FamilyRelationship.guardian_id == guardian_id,
                FamilyRelationship.status == RelationshipStatus.ACCEPTED
            )
        )

        # Apply search and filters
        if search:
            stmt = stmt.where(Document.title.ilike(f"%{search}%"))
        
        # Supporting both category and document_type (aliases)
        doc_type_filter = document_type or category
        if doc_type_filter:
            stmt = stmt.where(Document.document_type == doc_type_filter)

        if dependent_name:
            stmt = stmt.where(User.full_name.ilike(f"%{dependent_name}%"))

        if relationship:
            stmt = stmt.where(FamilyRelationship.relationship == relationship)

        if date_uploaded:
            try:
                # Format: YYYY-MM-DD
                target_date = date.fromisoformat(date_uploaded)
                stmt = stmt.where(func.date(Document.created_at) == target_date)
            except ValueError:
                pass # ignore invalid date format

        # Apply pagination
        offset = (page - 1) * limit
        stmt = stmt.order_by(Document.created_at.desc()).offset(offset).limit(limit)

        res = await db.execute(stmt)
        rows = res.all()

        # Group in memory by dependent
        grouped: Dict[uuid.UUID, DependentDocumentsResponse] = {}
        for doc_item, rel_item, user_item in rows:
            dep_id = user_item.id
            if dep_id not in grouped:
                grouped[dep_id] = DependentDocumentsResponse(
                    dependent_id=dep_id,
                    dependent_name=user_item.full_name,
                    relationship=rel_item.relationship,
                    documents=[]
                )
            
            # Map Document db model to response schema
            grouped[dep_id].documents.append(DocumentCreateResponse.model_validate(doc_item))

        return list(grouped.values())

async def asyncio_gather_summary_counts(db: AsyncSession, user_id: uuid.UUID) -> Tuple[int, int, int, int, int]:
    import asyncio
    # Run queries concurrently
    tasks = [
        FamilyRepository.count_active_relationships(db, user_id),
        FamilyRepository.count_guardians(db, user_id),
        FamilyRepository.count_dependents(db, user_id),
        FamilyRepository.count_pending_invitations(db, user_id)
    ]
    results = await asyncio.gather(*tasks)
    
    # Calculate accessible documents count for the guardian
    dependents = await FamilyRepository.get_dependents_for_guardian(db, user_id)
    dep_ids = [d.dependent_id for d in dependents]
    doc_count = 0
    if dep_ids:
        doc_count_stmt = select(func.count()).select_from(Document).where(Document.owner_id.in_(dep_ids))
        doc_count_res = await db.execute(doc_count_stmt)
        doc_count = doc_count_res.scalar() or 0

    return results[0], results[1], results[2], results[3], doc_count
