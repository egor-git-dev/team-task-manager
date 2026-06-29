from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app
from app.models.meetings import Meeting
from app.models.tasks import Task, TaskStatus
from app.models.users import User, UserRole
from app.services import calendar as calendar_services

client = TestClient(app)


def test_get_calendar_success(monkeypatch):
    async def fake_get_current_user():
        return User(id=1, team_id=10, role=UserRole.USER)

    starts_at = datetime.now(UTC)
    ends_at = starts_at + timedelta(days=1)

    tasks = [
        Task(
            id=1,
            title="task",
            description="task description",
            status=TaskStatus.OPEN,
            deadline=starts_at + timedelta(hours=1),
            creator_id=1,
            assignee_id=None,
            team_id=10,
            created_at=datetime.now(UTC),
        )
    ]
    meetings = [
        Meeting(
            id=1,
            title="meeting",
            description="meeting description",
            starts_at=starts_at + timedelta(hours=2),
            ends_at=starts_at + timedelta(hours=3),
            creator_id=1,
            participant_id=2,
            team_id=10,
            is_cancelled=False,
            created_at=datetime.now(UTC),
        )
    ]

    mock_get_calendar = AsyncMock(return_value={"tasks": tasks, "meetings": meetings})
    monkeypatch.setattr(calendar_services, "get_calendar", mock_get_calendar)

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.get(
            "/api/v1/calendar",
            params={
                "starts_at": starts_at.isoformat(),
                "ends_at": ends_at.isoformat(),
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "task"
    assert len(data["meetings"]) == 1
    assert data["meetings"][0]["title"] == "meeting"

    await_args = mock_get_calendar.await_args
    assert await_args is not None
    current_user, actual_starts_at, actual_ends_at, db = await_args.args
    assert current_user.id == 1
    assert actual_starts_at == starts_at
    assert actual_ends_at == ends_at


def test_get_calendar_invalid_range(monkeypatch):
    async def fake_get_current_user():
        return User(id=1, team_id=10, role=UserRole.USER)

    starts_at = datetime.now(UTC)
    ends_at = starts_at - timedelta(days=1)

    mock_get_calendar = AsyncMock()
    monkeypatch.setattr(calendar_services, "get_calendar", mock_get_calendar)

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.get(
            "/api/v1/calendar",
            params={
                "starts_at": starts_at.isoformat(),
                "ends_at": ends_at.isoformat(),
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert data["detail"] == "Invalid date range"
    mock_get_calendar.assert_not_awaited()
