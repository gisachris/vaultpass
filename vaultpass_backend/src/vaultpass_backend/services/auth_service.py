import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from vaultpass_backend.models.user import User
from vaultpass_backend.schemas.auth import RegisterRequest, LoginRequest
from vaultpass_backend.core.security import get_password_hash, verify_password

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Retrieve a user from the database by email address.
    """
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    """
    Retrieve a user from the database by UUID.
    """
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def register_user(db: AsyncSession, register_data: RegisterRequest) -> User:
    """
    Register a new user. Raises 409 Conflict if email is already taken.
    """
    existing_user = await get_user_by_email(db, register_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )
    
    hashed_password = get_password_hash(register_data.password)
    
    new_user = User(
        full_name=register_data.full_name,
        email=register_data.email,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    await db.flush()

    # Automatically create default settings row
    from vaultpass_backend.models.settings import UserSettings
    default_settings = UserSettings(user_id=new_user.id)
    db.add(default_settings)
    
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def authenticate_user(db: AsyncSession, login_data: LoginRequest) -> User:
    """
    Authenticate user by email and password. Raises 401 Unauthorized if invalid.
    """
    user = await get_user_by_email(db, login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address is not verified. Please check your inbox."
        )
    
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Update last login timestamp
    from sqlalchemy import func
    user.last_login = func.now()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def verify_email_token(db: AsyncSession, token: str) -> User:
    """
    Verify verification token and set user as verified.
    """
    from vaultpass_backend.core.security import verify_token
    payload = verify_token(token)
    if not payload or payload.get("type") != "verify":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload"
        )
    
    user = await get_user_by_id(db, uuid.UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        return user

    user.is_verified = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def generate_password_reset_token(db: AsyncSession, email: str) -> str:
    """
    Generate a password reset token for user with given email.
    """
    from datetime import timedelta
    from vaultpass_backend.core.security import create_access_token
    
    user = await get_user_by_email(db, email.lower().strip())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )
    
    # Reset token valid for 15 minutes
    token = create_access_token(
        data={"sub": str(user.id), "type": "reset"},
        expires_delta=timedelta(minutes=15)
    )
    return token


async def reset_password_with_token(db: AsyncSession, token: str, new_password: str) -> None:
    """
    Verify reset token and update user's password.
    """
    from vaultpass_backend.core.security import verify_token, get_password_hash
    payload = verify_token(token)
    if not payload or payload.get("type") != "reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload"
        )
    
    user = await get_user_by_id(db, uuid.UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.password_hash = get_password_hash(new_password)
    db.add(user)
    await db.commit()

