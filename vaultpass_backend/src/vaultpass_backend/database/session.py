from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from vaultpass_backend.database.connection import engine

# Create the session maker bound to our async engine
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)
