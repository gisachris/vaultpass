import ssl
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from vaultpass_backend.core.config import settings

# Create SSL context for Supabase (requires SSL connections)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Create async engine with SSL support
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args={
        "ssl": ssl_context,
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

# Declarative base class for models
Base = declarative_base()
