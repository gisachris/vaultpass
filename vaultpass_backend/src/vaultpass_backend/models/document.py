import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from vaultpass_backend.database.connection import Base

if TYPE_CHECKING:
    from vaultpass_backend.models.user import User
    from vaultpass_backend.models.document_share import DocumentShare

class DocumentType(str, enum.Enum):
    PASSPORT = "PASSPORT"
    NATIONAL_ID = "NATIONAL_ID"
    BIRTH_CERTIFICATE = "BIRTH_CERTIFICATE"
    ACADEMIC_CERTIFICATE = "ACADEMIC_CERTIFICATE"
    PROPERTY_DOCUMENT = "PROPERTY_DOCUMENT"
    WILL = "WILL"
    OTHER = "OTHER"

class Document(Base):
    """
    SQLAlchemy model representing the documents table.
    """
    __tablename__ = "documents"

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
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType, name="document_type_enum"),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    file_path: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    file_size: Mapped[int] = mapped_column(
        nullable=False
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    expiry_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
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
    owner: Mapped["User"] = relationship("User", back_populates="documents")
    shares: Mapped[List["DocumentShare"]] = relationship(
        "DocumentShare",
        back_populates="document",
        cascade="all, delete-orphan"
    )
