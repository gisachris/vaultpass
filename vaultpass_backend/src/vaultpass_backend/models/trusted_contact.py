import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship as sqla_relationship
from vaultpass_backend.database.connection import Base

if TYPE_CHECKING:
    from vaultpass_backend.models.user import User
    from vaultpass_backend.models.document_share import DocumentShare

class TrustedContact(Base):
    """
    SQLAlchemy model representing the trusted_contacts table.
    """
    __tablename__ = "trusted_contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )
    relationship: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )
    linked_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Unique constraint per owner and email address
    __table_args__ = (
        UniqueConstraint("owner_id", "email", name="uq_trusted_contacts_owner_email"),
    )

    # Relationships
    owner: Mapped["User"] = sqla_relationship("User", foreign_keys=[owner_id], back_populates="trusted_contacts")
    linked_user: Mapped[Optional["User"]] = sqla_relationship("User", foreign_keys=[linked_user_id], back_populates="trusted_contact_links")
    shares: Mapped[List["DocumentShare"]] = sqla_relationship(
        "DocumentShare",
        back_populates="contact",
        cascade="all, delete-orphan"
    )
