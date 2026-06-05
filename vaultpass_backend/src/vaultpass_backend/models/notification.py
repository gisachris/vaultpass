import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship as sqla_relationship
from vaultpass_backend.database.connection import Base

if TYPE_CHECKING:
    from vaultpass_backend.models.user import User
    from vaultpass_backend.models.document import Document
    from vaultpass_backend.models.trusted_contact import TrustedContact
    from vaultpass_backend.models.document_share import DocumentShare

class NotificationType(str, enum.Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"

class Notification(Base):
    """
    SQLAlchemy model representing the notifications table.
    """
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, name="notification_type_enum"),
        nullable=False
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
        nullable=False
    )
    related_document_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    related_contact_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("trusted_contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    related_share_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("document_shares.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = sqla_relationship("User", back_populates="notifications")
    document: Mapped["Document | None"] = sqla_relationship("Document")
    contact: Mapped["TrustedContact | None"] = sqla_relationship("TrustedContact")
    share: Mapped["DocumentShare | None"] = sqla_relationship("DocumentShare")
