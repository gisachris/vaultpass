import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from alembic.config import Config
from alembic import command

from vaultpass_backend.core.config import settings
from vaultpass_backend.api.auth import router as auth_router
from vaultpass_backend.api.documents import router as documents_router
from vaultpass_backend.api.trusted_contacts import router as trusted_contacts_router

logger = logging.getLogger("vaultpass")


def run_migrations() -> None:
    """
    Run Alembic migrations programmatically on application startup.
    This ensures the database schema is always up-to-date when the app boots.
    """
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations applied successfully.")
    except Exception as e:
        logger.error(f"Failed to apply database migrations: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan event handler.
    Runs migrations on startup and performs cleanup on shutdown.
    """
    logger.info("Starting VaultPass API...")
    import asyncio
    await asyncio.to_thread(run_migrations)
    logger.info("VaultPass API is ready.")
    yield
    logger.info("Shutting down VaultPass API...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(trusted_contacts_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Welcome to VaultPass API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
