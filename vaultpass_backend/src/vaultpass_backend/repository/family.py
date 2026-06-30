import uuid
from typing import List, Optional
from sqlalchemy import select, or_, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from vaultpass_backend.models.family_relationship import FamilyRelationship, RelationshipStatus

class FamilyRepository:
    @staticmethod
    async def create_relationship(db: AsyncSession, relationship: FamilyRelationship) -> FamilyRelationship:
        db.add(relationship)
        await db.commit()
        await db.refresh(relationship)
        return relationship

    @staticmethod
    async def get_relationship_by_id(db: AsyncSession, relationship_id: uuid.UUID) -> Optional[FamilyRelationship]:
        query = (
            select(FamilyRelationship)
            .where(FamilyRelationship.id == relationship_id)
            .options(
                selectinload(FamilyRelationship.guardian),
                selectinload(FamilyRelationship.dependent),
                selectinload(FamilyRelationship.inviter)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_or_pending_between_users(
        db: AsyncSession, user_a: uuid.UUID, user_b: uuid.UUID
    ) -> Optional[FamilyRelationship]:
        """
        Find any active (ACCEPTED) or PENDING relationship between two users
        in either direction (to prevent duplicates and circular guardianship).
        """
        query = (
            select(FamilyRelationship)
            .where(
                or_(
                    and_(FamilyRelationship.guardian_id == user_a, FamilyRelationship.dependent_id == user_b),
                    and_(FamilyRelationship.guardian_id == user_b, FamilyRelationship.dependent_id == user_a)
                )
            )
            .where(FamilyRelationship.status.in_([RelationshipStatus.PENDING, RelationshipStatus.ACCEPTED]))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_sent_invitations(db: AsyncSession, user_id: uuid.UUID) -> List[FamilyRelationship]:
        query = (
            select(FamilyRelationship)
            .where(FamilyRelationship.invited_by == user_id, FamilyRelationship.status == RelationshipStatus.PENDING)
            .options(
                selectinload(FamilyRelationship.guardian),
                selectinload(FamilyRelationship.dependent)
            )
            .order_by(FamilyRelationship.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_received_invitations(db: AsyncSession, user_id: uuid.UUID) -> List[FamilyRelationship]:
        """
        Get invitations where user is the invitee.
        Note: The dependent is invited by the guardian.
        So guardian_id is inviter, dependent_id is recipient.
        """
        query = (
            select(FamilyRelationship)
            .where(
                FamilyRelationship.dependent_id == user_id,
                FamilyRelationship.status == RelationshipStatus.PENDING,
                FamilyRelationship.invited_by != user_id
            )
            .options(
                selectinload(FamilyRelationship.guardian),
                selectinload(FamilyRelationship.dependent)
            )
            .order_by(FamilyRelationship.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_family_members(db: AsyncSession, user_id: uuid.UUID) -> List[FamilyRelationship]:
        """
        Get all accepted relationships where the user is either the guardian or the dependent.
        """
        query = (
            select(FamilyRelationship)
            .where(
                FamilyRelationship.status == RelationshipStatus.ACCEPTED,
                or_(FamilyRelationship.guardian_id == user_id, FamilyRelationship.dependent_id == user_id)
            )
            .options(
                selectinload(FamilyRelationship.guardian),
                selectinload(FamilyRelationship.dependent)
            )
            .order_by(FamilyRelationship.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_dependents_for_guardian(db: AsyncSession, guardian_id: uuid.UUID) -> List[FamilyRelationship]:
        query = (
            select(FamilyRelationship)
            .where(FamilyRelationship.guardian_id == guardian_id, FamilyRelationship.status == RelationshipStatus.ACCEPTED)
            .options(selectinload(FamilyRelationship.dependent))
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_guardians_for_dependent(db: AsyncSession, dependent_id: uuid.UUID) -> List[FamilyRelationship]:
        query = (
            select(FamilyRelationship)
            .where(FamilyRelationship.dependent_id == dependent_id, FamilyRelationship.status == RelationshipStatus.ACCEPTED)
            .options(selectinload(FamilyRelationship.guardian))
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def count_active_relationships(db: AsyncSession, user_id: uuid.UUID) -> int:
        query = (
            select(func.count())
            .select_from(FamilyRelationship)
            .where(
                FamilyRelationship.status == RelationshipStatus.ACCEPTED,
                or_(FamilyRelationship.guardian_id == user_id, FamilyRelationship.dependent_id == user_id)
            )
        )
        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def count_dependents(db: AsyncSession, guardian_id: uuid.UUID) -> int:
        query = (
            select(func.count())
            .select_from(FamilyRelationship)
            .where(FamilyRelationship.guardian_id == guardian_id, FamilyRelationship.status == RelationshipStatus.ACCEPTED)
        )
        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def count_guardians(db: AsyncSession, dependent_id: uuid.UUID) -> int:
        query = (
            select(func.count())
            .select_from(FamilyRelationship)
            .where(FamilyRelationship.dependent_id == dependent_id, FamilyRelationship.status == RelationshipStatus.ACCEPTED)
        )
        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def count_pending_invitations(db: AsyncSession, user_id: uuid.UUID) -> int:
        """
        Count pending invitations received by the user.
        """
        query = (
            select(func.count())
            .select_from(FamilyRelationship)
            .where(
                FamilyRelationship.dependent_id == user_id,
                FamilyRelationship.status == RelationshipStatus.PENDING,
                FamilyRelationship.invited_by != user_id
            )
        )
        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def check_is_guardian(db: AsyncSession, guardian_id: uuid.UUID, dependent_id: uuid.UUID) -> bool:
        query = (
            select(func.count())
            .select_from(FamilyRelationship)
            .where(
                FamilyRelationship.guardian_id == guardian_id,
                FamilyRelationship.dependent_id == dependent_id,
                FamilyRelationship.status == RelationshipStatus.ACCEPTED
            )
        )
        result = await db.execute(query)
        return (result.scalar() or 0) > 0
