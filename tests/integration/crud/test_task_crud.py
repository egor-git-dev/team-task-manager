from datetime import UTC, datetime

import pytest

from app.crud import tasks as task_crud
from app.models.tasks import Task
from app.models.teams import Team
from app.models.users import User
from app.schemas.tasks import TaskUpdate


@pytest.mark.asyncio
async def test_get_user_tasks(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    users = [
        User(email="egor@mail.com", hashed_password="12345678", team=team),
        User(email="ivan@mail.com", hashed_password="87654321", team=team),
    ]
    async_session.add_all([team, *users])
    await async_session.commit()
    for user in users:
        await async_session.refresh(user)

    tasks = [
        Task(
            title="Task 1",
            description="Description 1",
            creator_id=users[0].id,
            team_id=team.id,
        ),
        Task(
            title="Task 2",
            description="Description 2",
            creator_id=users[1].id,
            assignee_id=users[0].id,
            team_id=team.id,
        ),
        Task(
            title="Task 3",
            description="Description 3",
            creator_id=users[1].id,
            assignee_id=users[1].id,
            team_id=team.id,
        ),
    ]
    async_session.add_all(tasks)
    await async_session.commit()

    result = await task_crud.get_user_tasks(users[0].id, async_session)
    result_titles = {task.title for task in result}

    assert users[0].id is not None
    assert users[1].id is not None
    assert result_titles == {"Task 1", "Task 2"}
    assert len(result) == 2


@pytest.mark.asyncio
async def test_update_task(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    user = User(email="egor@mail.com", hashed_password="12345678", team=team)
    async_session.add_all([user, team])
    await async_session.commit()
    await async_session.refresh(user)

    task = Task(
        title="Old title",
        description="Old description",
        creator_id=user.id,
        team_id=team.id,
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)

    task_data = TaskUpdate(title="New title")
    await task_crud.update_task(task, task_data, async_session)

    assert task.title == "New title"
    assert task.description == "Old description"


@pytest.mark.asyncio
async def test_delete_task(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    user = User(email="egor@mail.com", hashed_password="12345678", team=team)
    async_session.add_all([user, team])
    await async_session.commit()
    await async_session.refresh(user)
    task = Task(
        title="Old title",
        description="Old description",
        creator_id=user.id,
        team_id=team.id,
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    task_id = task.id

    await task_crud.delete_task(task, async_session)

    assert await task_crud.get_task_by_id(task_id, async_session) is None
