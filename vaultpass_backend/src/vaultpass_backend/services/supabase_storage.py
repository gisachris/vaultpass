import httpx
from fastapi import UploadFile, HTTPException, status
from vaultpass_backend.core.config import settings

class SupabaseStorageService:
    def __init__(self):
        self.bucket = "vaultpass-documents"

    @property
    def url(self) -> str:
        return settings.SUPABASE_URL

    @property
    def key(self) -> str:
        return settings.SUPABASE_SERVICE_ROLE_KEY

    @property
    def base_api_url(self) -> str:
        return f"{self.url.rstrip('/')}/storage/v1"

    async def upload_file(self, file_path: str, file: UploadFile) -> dict:
        """
        Upload file to Supabase Storage bucket.
        file_path: The destination path in the bucket (e.g., 'user_id/uuid_filename.ext')
        """
        if not self.url or not self.key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase settings (URL/Key) are not configured."
            )

        headers = {
            "Authorization": f"Bearer {self.key}",
            "apikey": self.key,
            "Content-Type": file.content_type or "application/octet-stream"
        }
        
        # Read file content
        content = await file.read()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_api_url}/object/{self.bucket}/{file_path}",
                headers=headers,
                content=content,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload file to Supabase Storage: {response.text}"
                )
            
            return response.json()

    async def delete_file(self, file_path: str) -> None:
        """
        Delete file from Supabase Storage bucket.
        """
        if not self.url or not self.key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase settings (URL/Key) are not configured."
            )

        headers = {
            "Authorization": f"Bearer {self.key}",
            "apikey": self.key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_api_url}/object/{self.bucket}/{file_path}",
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code not in (200, 204):
                # Ignore 404 Not Found to prevent blocking the deletion flow if file is already deleted
                if response.status_code != 404:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to delete file from Supabase Storage: {response.text}"
                    )

    async def generate_signed_url(self, file_path: str, expires_in_seconds: int = 3600) -> str:
        """
        Generate a secure temporary download URL.
        """
        if not self.url or not self.key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase settings (URL/Key) are not configured."
            )

        headers = {
            "Authorization": f"Bearer {self.key}",
            "apikey": self.key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "expiresIn": expires_in_seconds
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_api_url}/object/sign/{self.bucket}/{file_path}",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to generate signed URL from Supabase Storage: {response.text}"
                )
            
            data = response.json()
            signed_url = data.get("signedURL") or data.get("signedUrl")
            if not signed_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Invalid response from Supabase Storage sign endpoint: {data}"
                )
            
            if signed_url.startswith("/"):
                signed_url = f"{self.url.rstrip('/')}{signed_url}"
            return signed_url

storage_service = SupabaseStorageService()
