from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meetings import Meeting
from app.models.tasks import Task
from app.models.users import User, UserRole
from app.services import calendar as calendar_services


@pytest.mark.asyncio
async def test_get_calendar_for_regular_user(monkeypatch):
    starts_at = datetime.now(UTC)
    ends_at = starts_at + timedelta(days=1)
    current_user = User(id=1, team_id=10, role=UserRole.USER)
    db = AsyncMock(spec=AsyncSession)

    tasks = [Task(id=1, title="task", creator_id=1, team_id=10)]
    meetings = [
        Meeting(id=1, title="meeting", creator_id=1, participant_id=2, team_id=10)
    ]

    mock_get_user_calendar_tasks = AsyncMock(return_value=tasks)
    mock_get_team_calendar_tasks = AsyncMock()
    mock_get_user_calendar_meetings = AsyncMock(return_value=meetings)

    monkeypatch.setattr(
        calendar_services.calendar_crud,
        "get_user_calendar_tasks",
        mock_get_user_calendar_tasks,
    )
    monkeypatch.setattr(
        calendar_services.calendar_crud,
        "get_team_calendar_tasks",
        mock_get_team_calendar_tasks,
    )
    monkeypatch.setattr(
        calendar_services.calendar_crud,
        "get_user_calendar_meetings",
        mock_get_user_calendar_meetings,
    )

    result = await calendar_services.get_calendar(current_user, starts_at, ends_at, db)

    assert result == {"tasks": tasks, "meetings": meetings}
    mock_get_user_calendar_tasks.assert_awaited_once_with(
        current_user.id, starts_at, ends_at, db
    )
    mock_get_team_calendar_tasks.assert_not_awaited()
    mock_get_user_calendar_meetings.assert_awaited_once_with(
        current_user.id, starts_at, ends_at, db
    )


@pytest.mark.asyncio
async def test_get_calendar_for_manager(monkeypatch):
    starts_at = datetime.now(UTC)
    ends_at = starts_at + timedelta(days=1)
    current_user = User(id=1, team_id=10, role=UserRole.MANAGER)
    db = AsyncMock(spec=AsyncSession)

    tasks = [Task(id=1, title="team task", creator_id=2, team_id=10)]
    meetings = [
        Meeting(id=1, title="meeting", creator_id=1, participant_id=2, team_id=10)
    ]

    mock_get_user_calendar_tasks = AsyncMock()
    mock_get_team_calendar_tasks = AsyncMock(return_value=tasks)
    mock_get_user_calendar_meetings = AsyncMock(return_value=meetings)

    monkeypatch.setattr(
        calendar_services.calendar_crud,
        "get_user_calendar_tasks",
        mock_get_user_calendar_tasks,
    )
    monkeypatch.setattr(
        calendar_services.calendar_crud,
        "get_team_calendar_tasks",
        mock_get_team_calendar_tasks,
    )
    monkeypatch.setattr(
        calendar_services.calendar_crud,
        "get_user_calendar_meetings",
        mock_get_user_calendar_meetings,
    )

    result = await calendar_services.get_calendar(current_user, starts_at, ends_at, db)

    assert result == {"tasks": tasks, "meetings": meetings}
    mock_get_team_calendar_tasks.assert_awaited_once_with(
        current_user.team_id, starts_at, ends_at, db
    )
    mock_get_user_calendar_tasks.assert_not_awaited()
    mock_get_user_calendar_meetings.assert_awaited_once_with(
        current_user.id, starts_at, ends_at, db
    )
