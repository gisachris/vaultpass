from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from vaultpass_backend.core.dependencies import get_db, get_current_user
from vaultpass_backend.models.user import User
from vaultpass_backend.schemas.settings import (
    ProfileSettingsResponse,
    ProfileSettingsUpdate,
    SecuritySettingsResponse,
    SecuritySettingsUpdate,
    NotificationSettingsResponse,
    NotificationSettingsUpdate,
    PrivacySettingsResponse,
    PrivacySettingsUpdate,
    ReminderSettingsResponse,
    ReminderSettingsUpdate,
    ChangePasswordRequest,
    DeactivateRequest,
    AccountInfoResponse,
)
from vaultpass_backend.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get(
    "/profile",
    response_model=ProfileSettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user profile settings",
)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await SettingsService.get_profile(db, current_user)

@router.put(
    "/profile",
    response_model=ProfileSettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update profile settings",
)
async def update_profile(
    request: Request,
    profile_data: ProfileSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await SettingsService.update_profile(
        db, current_user, profile_data, ip_address, user_agent
    )

@router.get(
    "/security",
    response_model=SecuritySettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get security settings",
)
async def get_security(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await SettingsService.get_security(db, current_user.id)

@router.put(
    "/security",
    response_model=SecuritySettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update security settings",
)
async def update_security(
    request: Request,
    security_data: SecuritySettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await SettingsService.update_security(
        db, current_user.id, security_data, ip_address, user_agent
    )

@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change user password",
)
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    await SettingsService.change_password(
        db, current_user, password_data, ip_address, user_agent
    )
    return {"message": "Your account password was changed"}

@router.get(
    "/notifications",
    response_model=NotificationSettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get notification settings",
)
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await SettingsService.get_notifications(db, current_user.id)

@router.put(
    "/notifications",
    response_model=NotificationSettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update notification settings",
)
async def update_notifications(
    request: Request,
    notifications_data: NotificationSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await SettingsService.update_notifications(
        db, current_user.id, notifications_data, ip_address, user_agent
    )

@router.get(
    "/privacy",
    response_model=PrivacySettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get privacy settings",
)
async def get_privacy(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await SettingsService.get_privacy(db, current_user.id)

@router.put(
    "/privacy",
    response_model=PrivacySettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update privacy settings",
)
async def update_privacy(
    request: Request,
    privacy_data: PrivacySettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await SettingsService.update_privacy(
        db, current_user.id, privacy_data, ip_address, user_agent
    )

@router.get(
    "/reminders",
    response_model=ReminderSettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document reminder settings",
)
async def get_reminders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await SettingsService.get_reminders(db, current_user.id)

@router.put(
    "/reminders",
    response_model=ReminderSettingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Update document reminder settings",
)
async def update_reminders(
    request: Request,
    reminders_data: ReminderSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await SettingsService.update_reminders(
        db, current_user.id, reminders_data, ip_address, user_agent
    )

@router.get(
    "/account",
    response_model=AccountInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Get account information",
)
async def get_account_info(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await SettingsService.get_account_info(db, current_user)

@router.get(
    "/export",
    status_code=status.HTTP_200_OK,
    summary="Export account settings",
)
async def export_settings(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await SettingsService.export_settings(db, current_user, ip_address, user_agent)

@router.post(
    "/deactivate",
    status_code=status.HTTP_200_OK,
    summary="Deactivate account",
)
async def deactivate_account(
    request: Request,
    deactivate_data: DeactivateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    await SettingsService.deactivate_account(
        db, current_user, deactivate_data, ip_address, user_agent
    )
    return {"message": "Account deactivated successfully"}
