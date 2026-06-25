import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship as orm_relationship
from vaultpass_backend.database.connection import Base

class RelationshipType(str, enum.Enum):
    PARENT = "PARENT"
    CHILD = "CHILD"
    GUARDIAN = "GUARDIAN"
    DEPENDENT = "DEPENDENT"
    SPOUSE = "SPOUSE"
    SIBLING = "SIBLING"
    OTHER = "OTHER"

class RelationshipStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    REMOVED = "REMOVED"

class FamilyRelationship(Base):
    """
    SQLAlchemy model representing the family_relationships table.
    """
    __tablename__ = "family_relationships"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    guardian_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    dependent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    relationship: Mapped[RelationshipType] = mapped_column(
        SQLEnum(RelationshipType, name="relationship_type_enum"),
        nullable=False
    )
    status: Mapped[RelationshipStatus] = mapped_column(
        SQLEnum(RelationshipStatus, name="relationship_status_enum"),
        default=RelationshipStatus.PENDING,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    invited_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Relationships using the alias orm_relationship to avoid column name shadowing
    # Added overlaps parameter to suppress SQLAlchemy warning
    guardian = orm_relationship("User", foreign_keys=[guardian_id], overlaps="family_dependents")
    dependent = orm_relationship("User", foreign_keys=[dependent_id], overlaps="family_guardians")
    inviter = orm_relationship("User", foreign_keys=[invited_by])
