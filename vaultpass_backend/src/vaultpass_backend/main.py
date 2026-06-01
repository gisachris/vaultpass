from fastapi import FastAPI
from vaultpass_backend.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.get("/")
def root():
    return {"message": "Welcome to VaultPass API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
