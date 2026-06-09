from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from vaultpass_backend.core.dependencies import get_db, get_current_user
from vaultpass_backend.models.user import User
from vaultpass_backend.schemas.dashboard import DashboardResponse
from vaultpass_backend.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user dashboard",
    description=(
        "Returns a complete aggregated dashboard snapshot for the authenticated user. "
        "Includes summary cards, document health, category breakdown, expiring documents, "
        "recent activity, recent notifications, and account overview. "
        "All data is scoped exclusively to the current user."
    ),
)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardResponse:
    return await DashboardService.get_dashboard(db, current_user)
