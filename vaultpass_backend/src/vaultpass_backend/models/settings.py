import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from vaultpass_backend.database.connection import Base

if TYPE_CHECKING:
    from vaultpass_backend.models.user import User

class UserSettings(Base):
    """
    SQLAlchemy model representing the user_settings table.
    """
    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    push_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    document_expiry_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    shared_access_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    trusted_contact_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    security_alert_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    weekly_summary_notifications: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    session_timeout_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    document_reminder_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    allow_profile_visibility: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_contact_visibility: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    auto_logout_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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
    user: Mapped["User"] = relationship("User", back_populates="settings")
