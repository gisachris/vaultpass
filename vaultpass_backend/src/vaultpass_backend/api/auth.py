from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.core.dependencies import get_db, get_current_user
from vaultpass_backend.schemas.auth import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from vaultpass_backend.services import auth_service
from vaultpass_backend.core.security import create_access_token
from vaultpass_backend.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    response_description="Success confirmation message"
)
async def register(
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user account:
    - Validates input full name, email, and password strength
    - Checks for duplicate emails (409 Conflict)
    - Hashes password using Bcrypt
    - Saves user to PostgreSQL database
    """
    await auth_service.register_user(db, register_data)
    return {"message": "Account created successfully"}

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    response_description="Access token and authenticated user profile"
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user credentials:
    - Validates password (401 Unauthorized for invalid email or password)
    - Generates standard HS256 JWT access token with 24-hour expiration
    - Returns token payload along with base user credentials
    """
    user = await auth_service.authenticate_user(db, login_data)
    
    # Encode user ID as the subject
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    response_description="Authenticated user details"
)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve user metadata for the currently active session using standard JWT authorization header.
    """
    return UserResponse.model_validate(current_user)
