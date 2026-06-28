from datetime import UTC, datetime, timedelta

import pytest

from app.crud import calendar as calendar_crud
from app.models.meetings import Meeting
from app.models.tasks import Task
from app.models.teams import Team
from app.models.users import User


@pytest.mark.asyncio
async def test_get_user_calendar_tasks(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    user = User(email="user@example.com", hashed_password="hashed", team=team)
    other_user = User(email="other@example.com", hashed_password="hashed", team=team)
    async_session.add_all([team, user, other_user])
    await async_session.commit()
    await async_session.refresh(user)
    await async_session.refresh(other_user)
    await async_session.refresh(team)

    starts_at = datetime.now(UTC)
    ends_at = starts_at + timedelta(days=1)

    tasks = [
        Task(
            title="created by user",
            creator_id=user.id,
            team_id=team.id,
            deadline=starts_at + timedelta(hours=1),
        ),
        Task(
            title="assigned to user",
            creator_id=other_user.id,
            assignee_id=user.id,
            team_id=team.id,
            deadline=starts_at + timedelta(hours=2),
        ),
        Task(
            title="other user task",
            creator_id=other_user.id,
            team_id=team.id,
            deadline=starts_at + timedelta(hours=3),
        ),
        Task(
            title="outside period",
            creator_id=user.id,
            team_id=team.id,
            deadline=ends_at + timedelta(hours=1),
        ),
        Task(
            title="without deadline",
            creator_id=user.id,
            team_id=team.id,
            deadline=None,
        ),
    ]
    async_session.add_all(tasks)
    await async_session.commit()

    result = await calendar_crud.get_user_calendar_tasks(
        user.id, starts_at, ends_at, async_session
    )
    result_titles = {task.title for task in result}

    assert result_titles == {"created by user", "assigned to user"}


@pytest.mark.asyncio
async def test_get_team_calendar_tasks(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    other_team = Team(
        name="other team", join_code="TEST4321", created_at=datetime.now(UTC)
    )
    user = User(email="user@example.com", hashed_password="hashed", team=team)
    other_user = User(
        email="other@example.com", hashed_password="hashed", team=other_team
    )
    async_session.add_all([team, other_team, user, other_user])
    await async_session.commit()
    await async_session.refresh(user)
    await async_session.refresh(other_user)
    await async_session.refresh(team)
    await async_session.refresh(other_team)

    starts_at = datetime.now(UTC)
    ends_at = starts_at + timedelta(days=1)

    tasks = [
        Task(
            title="team task",
            creator_id=user.id,
            team_id=team.id,
            deadline=starts_at + timedelta(hours=1),
        ),
        Task(
            title="other team task",
            creator_id=other_user.id,
            team_id=other_team.id,
            deadline=starts_at + timedelta(hours=2),
        ),
        Task(
            title="outside period",
            creator_id=user.id,
            team_id=team.id,
            deadline=ends_at + timedelta(hours=1),
        ),
    ]
    async_session.add_all(tasks)
    await async_session.commit()

    result = await calendar_crud.get_team_calendar_tasks(
        team.id, starts_at, ends_at, async_session
    )
    result_titles = {task.title for task in result}

    assert result_titles == {"team task"}


@pytest.mark.asyncio
async def test_get_user_calendar_meetings(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    user = User(email="user@example.com", hashed_password="hashed", team=team)
    other_user = User(email="other@example.com", hashed_password="hashed", team=team)
    async_session.add_all([team, user, other_user])
    await async_session.commit()
    await async_session.refresh(user)
    await async_session.refresh(other_user)
    await async_session.refresh(team)

    starts_at = datetime.now(UTC)
    ends_at = starts_at + timedelta(days=1)

    meetings = [
        Meeting(
            title="created by user",
            starts_at=starts_at + timedelta(hours=1),
            ends_at=starts_at + timedelta(hours=2),
            creator_id=user.id,
            participant_id=other_user.id,
            team_id=team.id,
        ),
        Meeting(
            title="user is participant",
            starts_at=starts_at + timedelta(hours=3),
            ends_at=starts_at + timedelta(hours=4),
            creator_id=other_user.id,
            participant_id=user.id,
            team_id=team.id,
        ),
        Meeting(
            title="cancelled meeting",
            starts_at=starts_at + timedelta(hours=5),
            ends_at=starts_at + timedelta(hours=6),
            creator_id=user.id,
            participant_id=other_user.id,
            team_id=team.id,
            is_cancelled=True,
        ),
        Meeting(
            title="other users meeting",
            starts_at=starts_at + timedelta(hours=7),
            ends_at=starts_at + timedelta(hours=8),
            creator_id=other_user.id,
            participant_id=other_user.id,
            team_id=team.id,
        ),
        Meeting(
            title="outside period",
            starts_at=ends_at + timedelta(hours=1),
            ends_at=ends_at + timedelta(hours=2),
            creator_id=user.id,
            participant_id=other_user.id,
            team_id=team.id,
        ),
    ]
    async_session.add_all(meetings)
    await async_session.commit()

    result = await calendar_crud.get_user_calendar_meetings(
        user.id, starts_at, ends_at, async_session
    )
    result_titles = {meeting.title for meeting in result}

    assert result_titles == {"created by user", "user is participant"}
