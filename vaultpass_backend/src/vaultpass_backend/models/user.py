import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import String, Text, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from vaultpass_backend.database.connection import Base

if TYPE_CHECKING:
    from vaultpass_backend.models.document import Document
    from vaultpass_backend.models.trusted_contact import TrustedContact
    from vaultpass_backend.models.document_share import DocumentShare
    from vaultpass_backend.models.notification import Notification
    from vaultpass_backend.models.settings import UserSettings

class User(Base):
    """
    SQLAlchemy model representing the users table.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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

    # Relationships
    settings: Mapped["UserSettings"] = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    trusted_contacts: Mapped[List["TrustedContact"]] = relationship(
        "TrustedContact",
        foreign_keys="TrustedContact.owner_id",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    trusted_contact_links: Mapped[List["TrustedContact"]] = relationship(
        "TrustedContact",
        foreign_keys="TrustedContact.linked_user_id",
        back_populates="linked_user",
    )
    shares: Mapped[List["DocumentShare"]] = relationship(
        "DocumentShare",
        foreign_keys="DocumentShare.owner_id",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    received_shares: Mapped[List["DocumentShare"]] = relationship(
        "DocumentShare",
        foreign_keys="DocumentShare.recipient_user_id",
        back_populates="recipient_user",
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )

