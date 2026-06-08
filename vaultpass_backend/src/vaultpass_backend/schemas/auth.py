import re
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterRequest(BaseModel):
    """
    Schema for user registration requests.
    """
    full_name: str = Field(..., min_length=3, description="User's full name (minimum 3 characters)")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        return v

class LoginRequest(BaseModel):
    """
    Schema for user login requests.
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class UserResponse(BaseModel):
    """
    Schema for returning user information.
    """
    id: UUID
    full_name: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }

class TokenResponse(BaseModel):
    """
    Schema for login response containing the JWT and user info.
    """
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
