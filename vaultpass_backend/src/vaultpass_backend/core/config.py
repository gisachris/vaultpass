from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "VaultPass API"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/vaultpass"
    
    JWT_SECRET_KEY: str = "supersecretkeythatisnotsecuretokeepinversioncontrol"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    CORS_ORIGIN_REGEX: str | None = None

    # Supabase Storage settings
    SUPABASE_URL: str = "https://crzevbgduvewwpwyaqfa.supabase.co"
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()

