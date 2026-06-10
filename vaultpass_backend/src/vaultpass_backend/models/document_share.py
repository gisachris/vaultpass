import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from vaultpass_backend.database.connection import Base

if TYPE_CHECKING:
    from vaultpass_backend.models.user import User
    from vaultpass_backend.models.document import Document
    from vaultpass_backend.models.trusted_contact import TrustedContact

class DocumentShare(Base):
    """
    SQLAlchemy model representing the document_shares table.
    """
    __tablename__ = "document_shares"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    contact_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trusted_contacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    access_token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    last_accessed_at: Mapped[datetime | None] = mapped_column(
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
    recipient_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    access_level: Mapped[str | None] = mapped_column(
        String(50),
        default="view",
        nullable=True
    )
    allow_download: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )


    # Relationships
    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id], back_populates="shares")
    recipient_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[recipient_user_id], back_populates="received_shares")
    document: Mapped["Document"] = relationship("Document", back_populates="shares")
    contact: Mapped["TrustedContact"] = relationship("TrustedContact", back_populates="shares")

    @property
    def share_link(self) -> str:
        """
        Dynamically computes the frontend secure link for this share token.
        """
        return f"https://vaultpass.app/shared/{self.access_token}"
