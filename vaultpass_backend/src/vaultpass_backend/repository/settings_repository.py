import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from vaultpass_backend.models.settings import UserSettings

class SettingsRepository:
    """
    Repository class encapsulating database operations for UserSettings.
    """

    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[UserSettings]:
        """
        Retrieve settings for a user.
        """
        query = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, settings: UserSettings) -> UserSettings:
        """
        Create a new settings record. Uses add/flush/refresh.
        """
        db.add(settings)
        await db.flush()
        await db.refresh(settings)
        return settings

    @staticmethod
    async def save(db: AsyncSession, settings: UserSettings) -> UserSettings:
        """
        Save/update an existing settings record.
        """
        await db.flush()
        await db.refresh(settings)
        return settings
