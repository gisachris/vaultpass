import uuid
from datetime import datetime, timezone, timedelta
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from vaultpass_backend.main import app
from vaultpass_backend.models.user import User

client = TestClient(app)

# ===================== FIXTURES =====================

@pytest.fixture
def mock_user():
    user = User(
        id=uuid.uuid4(),
        full_name="Jane Vault",
        email="jane@vaultpass.com",
        password_hash="hashed",
        is_active=True,
        created_at=datetime.now(timezone.utc) - timedelta(days=90),
        last_login=datetime.now(timezone.utc) - timedelta(hours=2),
    )
    return user


@pytest.fixture
def override_auth_dependency(mock_user):
    from vaultpass_backend.core.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


def _make_dashboard_response(user):
    """Build a complete DashboardResponse dict for mocking."""
    from vaultpass_backend.schemas.dashboard import (
        DashboardResponse,
        SummaryResponse,
        DocumentHealthResponse,
        CategoryBreakdownResponse,
        ExpiringDocumentResponse,
        RecentActivityResponse,
        RecentNotificationResponse,
        SharedWithMeDocumentResponse,
        AccountOverviewResponse,
    )

    now = datetime.now(timezone.utc)
    doc_id = uuid.uuid4()
    notif_id = uuid.uuid4()
    share_id = uuid.uuid4()

    return DashboardResponse(
        summary=SummaryResponse(
            total_documents=10,
            trusted_contacts=3,
            active_shares=2,
            unread_notifications=4,
            shared_with_me_count=2,
        ),
        document_health=DocumentHealthResponse(
            valid_documents=7,
            expiring_soon=2,
            expired_documents=1,
        ),
        categories=[
            CategoryBreakdownResponse(category="PASSPORT", count=5),
            CategoryBreakdownResponse(category="NATIONAL_ID", count=3),
            CategoryBreakdownResponse(category="WILL", count=2),
        ],
        expiring_documents=[
            ExpiringDocumentResponse(
                document_id=doc_id,
                document_name="My Passport",
                category="PASSPORT",
                expiry_date=now + timedelta(days=15),
                days_remaining=15,
            )
        ],
        recent_activity=[
            RecentActivityResponse(
                action="DOCUMENT_CREATED",
                description="Document 'Passport' uploaded.",
                created_at=now - timedelta(hours=1),
            )
        ],
        recent_notifications=[
            RecentNotificationResponse(
                id=notif_id,
                title="Document Uploaded",
                message="Passport uploaded successfully.",
                is_read=False,
                created_at=now - timedelta(hours=1),
            )
        ],
        recent_shared_documents=[
            SharedWithMeDocumentResponse(
                share_id=share_id,
                document_title="Insurance.pdf",
                owner_name="John Doe",
                shared_at=now - timedelta(hours=3),
            )
        ],
        account_overview=AccountOverviewResponse(
            account_created=user.created_at,
            last_login=user.last_login,
            storage_used_mb=12.5,
        ),
    )


# ===================== ROUTER TESTS =====================

@patch(
    "vaultpass_backend.api.dashboard_router.DashboardService.get_dashboard",
    new_callable=AsyncMock,
)
def test_dashboard_loads_successfully(mock_get_dashboard, override_auth_dependency, mock_user):
    """GET /api/dashboard/ should return 200 with all sections present."""
    mock_get_dashboard.return_value = _make_dashboard_response(mock_user)

    response = client.get("/api/dashboard/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "summary" in data
    assert "document_health" in data
    assert "categories" in data
    assert "expiring_documents" in data
    assert "recent_activity" in data
    assert "recent_notifications" in data
    assert "recent_shared_documents" in data
    assert "account_overview" in data


@patch(
    "vaultpass_backend.api.dashboard_router.DashboardService.get_dashboard",
    new_callable=AsyncMock,
)
def test_summary_counts_correct(mock_get_dashboard, override_auth_dependency, mock_user):
    """Summary card values should match what the service returns."""
    mock_get_dashboard.return_value = _make_dashboard_response(mock_user)

    response = client.get("/api/dashboard/")
    summary = response.json()["summary"]
    assert summary["total_documents"] == 10
    assert summary["trusted_contacts"] == 3
    assert summary["active_shares"] == 2
    assert summary["unread_notifications"] == 4
    assert summary["shared_with_me_count"] == 2


@patch(
    "vaultpass_backend.api.dashboard_router.DashboardService.get_dashboard",
    new_callable=AsyncMock,
)
def test_document_health_correct(mock_get_dashboard, override_auth_dependency, mock_user):
    """Document health section should expose valid, expiring, and expired counts."""
    mock_get_dashboard.return_value = _make_dashboard_response(mock_user)

    response = client.get("/api/dashboard/")
    health = response.json()["document_health"]
    assert health["valid_documents"] == 7
    assert health["expiring_soon"] == 2
    assert health["expired_documents"] == 1


@patch(
    "vaultpass_backend.api.dashboard_router.DashboardService.get_dashboard",
    new_callable=AsyncMock,
)
def test_category_aggregation_correct(mock_get_dashboard, override_auth_dependency, mock_user):
    """Categories should be sorted descending by count."""
    mock_get_dashboard.return_value = _make_dashboard_response(mock_user)

    response = client.get("/api/dashboard/")
    categories = response.json()["categories"]
    assert len(categories) == 3
    assert categories[0]["category"] == "PASSPORT"
    assert categories[0]["count"] == 5
    # Verify descending order
    counts = [c["count"] for c in categories]
    assert counts == sorted(counts, reverse=True)


@patch(
    "vaultpass_backend.api.dashboard_router.DashboardService.get_dashboard",
    new_callable=AsyncMock,
)
def test_expiring_documents_correct(mock_get_dashboard, override_auth_dependency, mock_user):
    """Expiring documents should include days_remaining and be soonest-first."""
    mock_get_dashboard.return_value = _make_dashboard_response(mock_user)

    response = client.get("/api/dashboard/")
    expiring = response.json()["expiring_documents"]
    assert len(expiring) == 1
    assert expiring[0]["document_name"] == "My Passport"
    assert expiring[0]["days_remaining"] == 15
    assert "expiry_date" in expiring[0]


@patch(
    "vaultpass_backend.api.dashboard_router.DashboardService.get_dashboard",
    new_callable=AsyncMock,
)
def test_recent_activity_retrieval(mock_get_dashboard, override_auth_dependency, mock_user):
    """Recent activity should be present and contain audit log fields."""
    mock_get_dashboard.return_value = _make_dashboard_response(mock_user)

    response = client.get("/api/dashboard/")
    activity = response.json()["recent_activity"]
    assert len(activity) == 1
    assert activity[0]["action"] == "DOCUMENT_CREATED"
    assert "description" in activity[0]
    assert "created_at" in activity[0]


@patch(
    "vaultpass_backend.api.dashboard_router.DashboardService.get_dashboard",
    new_callable=AsyncMock,
)
def test_recent_notifications_retrieval(mock_get_dashboard, override_auth_dependency, mock_user):
    """Recent notifications should expose id, title, message, is_read, created_at."""
    mock_get_dashboard.return_value = _make_dashboard_response(mock_user)

    response = client.get("/api/dashboard/")
    notifications = response.json()["recent_notifications"]
    assert len(notifications) == 1
    n = notifications[0]
    assert n["title"] == "Document Uploaded"
    assert n["is_read"] is False
    assert "id" in n
    assert "created_at" in n


@patch(
    "vaultpass_backend.api.dashboard_router.DashboardService.get_dashboard",
    new_callable=AsyncMock,
)
def test_empty_dashboard(mock_get_dashboard, override_auth_dependency, mock_user):
    """An account with no data should return zeros and empty lists, not errors."""
    from vaultpass_backend.schemas.dashboard import (
        DashboardResponse, SummaryResponse, DocumentHealthResponse,
        AccountOverviewResponse,
    )
    mock_get_dashboard.return_value = DashboardResponse(
        summary=SummaryResponse(
            total_documents=0,
            trusted_contacts=0,
            active_shares=0,
            unread_notifications=0,
            shared_with_me_count=0,
        ),
        document_health=DocumentHealthResponse(
            valid_documents=0,
            expiring_soon=0,
            expired_documents=0,
        ),
        categories=[],
        expiring_documents=[],
        recent_activity=[],
        recent_notifications=[],
        recent_shared_documents=[],
        account_overview=AccountOverviewResponse(
            account_created=mock_user.created_at,
            last_login=None,
            storage_used_mb=0.0,
        ),
    )

    response = client.get("/api/dashboard/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["summary"]["total_documents"] == 0
    assert data["categories"] == []
    assert data["expiring_documents"] == []
    assert data["recent_activity"] == []
    assert data["recent_notifications"] == []
    assert data["account_overview"]["storage_used_mb"] == 0.0


def test_authorization_required():
    """Requests without an auth token should be rejected with 401."""
    # No override_auth_dependency fixture — dependency uses real token logic
    response = client.get("/api/dashboard/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_invalid_token_rejected():
    """Malformed bearer tokens should result in 401."""
    response = client.get(
        "/api/dashboard/",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@patch(
    "vaultpass_backend.api.dashboard_router.DashboardService.get_dashboard",
    new_callable=AsyncMock,
)
def test_user_isolation(mock_get_dashboard, mock_user):
    """Service must always be called with current_user, never leaking cross-user data."""
    from vaultpass_backend.core.dependencies import get_current_user

    # Override with user A
    user_a = mock_user
    app.dependency_overrides[get_current_user] = lambda: user_a

    mock_get_dashboard.return_value = _make_dashboard_response(user_a)

    response = client.get("/api/dashboard/")
    assert response.status_code == status.HTTP_200_OK

    # Verify get_dashboard was called with the correct user object
    called_user = mock_get_dashboard.call_args[0][1]  # second positional arg (user)
    assert called_user.id == user_a.id

    app.dependency_overrides.pop(get_current_user, None)


@patch(
    "vaultpass_backend.api.dashboard_router.DashboardService.get_dashboard",
    new_callable=AsyncMock,
)
def test_dashboard_shared_with_me_count(mock_get_dashboard, override_auth_dependency, mock_user):
    """Dashboard summary must include shared_with_me_count and recent_shared_documents."""
    mock_get_dashboard.return_value = _make_dashboard_response(mock_user)

    response = client.get("/api/dashboard/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["summary"]["shared_with_me_count"] == 2
    assert "recent_shared_documents" in data
    assert len(data["recent_shared_documents"]) == 1
    assert data["recent_shared_documents"][0]["document_title"] == "Insurance.pdf"
    assert data["recent_shared_documents"][0]["owner_name"] == "John Doe"
