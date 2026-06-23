from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tasks import Task
from app.schemas.tasks import TaskCreate
from app.services import tasks as task_services


@pytest.mark.asyncio
async def test_create_task(monkeypatch):
    task = Task(title="test_title", description="test_description")
    mock_create_task = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "create_task", mock_create_task)
    db = AsyncMock(spec=AsyncSession)
    task_data = TaskCreate(
        title="test_title",
        description="test_description",
    )
    creator_id = 1

    result = await task_services.create_task(task_data, creator_id, db)

    assert result is task
    mock_create_task.assert_awaited_once_with(task_data, creator_id, db)


@pytest.mark.asyncio
async def test_get_task_by_id_or_raise_success(monkeypatch):
    task = Task(title="test_title", description="test_description")
    mock_get_task_by_id = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "get_task_by_id", mock_get_task_by_id)
    db = AsyncMock(spec=AsyncSession)
    task_id = 1

    result = await task_services.get_task_by_id_or_raise(task_id, db)

    assert result is task
    mock_get_task_by_id.assert_awaited_once_with(task_id, db)


@pytest.mark.asyncio
async def test_get_task_by_id_or_raise_error(monkeypatch):
    mock_get_task_by_id = AsyncMock(return_value=None)
    monkeypatch.setattr(task_services.task_crud, "get_task_by_id", mock_get_task_by_id)
    db = AsyncMock(spec=AsyncSession)
    task_id = 1
    with pytest.raises(task_services.TaskNotFoundError):
        await task_services.get_task_by_id_or_raise(task_id, db)
    mock_get_task_by_id.assert_awaited_once_with(task_id, db)


@pytest.mark.asyncio
async def test_get_user_tasks(monkeypatch):
    tasks = [
        Task(title="test_title", description="test_description"),
        Task(title="test_title2", description="test_description2"),
    ]
    mock_get_user_tasks = AsyncMock(return_value=tasks)
    monkeypatch.setattr(task_services.task_crud, "get_user_tasks", mock_get_user_tasks)
    db = AsyncMock(spec=AsyncSession)
    user_id = 1

    result = await task_services.get_user_tasks(user_id, db)

    assert result is tasks
    mock_get_user_tasks.assert_awaited_once_with(user_id, db)
