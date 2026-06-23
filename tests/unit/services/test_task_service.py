from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tasks import Task
from app.models.users import User
from app.schemas.tasks import TaskCreate, TaskUpdate
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


@pytest.mark.asyncio
async def test_update_task_success(monkeypatch):
    task = Task(title="old title", description="old description", creator_id=1)
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_update_task = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "update_task", mock_update_task)
    task_id = 1
    task_data = TaskUpdate(title="new title", description="new description")
    current_user = User(id=1)
    db = AsyncMock(spec=AsyncSession)
    result = await task_services.update_task_or_raise(
        task_id, task_data, current_user, db
    )

    assert result is task
    mock_get_task_by_id_or_raise.assert_awaited_once_with(task_id, db)
    mock_update_task.assert_awaited_once_with(task, task_data, db)


@pytest.mark.asyncio
async def test_update_task_not_found(monkeypatch):
    mock_get_task_by_id_or_raise = AsyncMock(
        side_effect=task_services.TaskNotFoundError()
    )
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_update_task = AsyncMock()
    monkeypatch.setattr(task_services.task_crud, "update_task", mock_update_task)
    task_id = 1
    task_data = TaskUpdate(title="new title", description="new description")
    current_user = User(id=1)
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskNotFoundError):
        await task_services.update_task_or_raise(task_id, task_data, current_user, db)
    mock_update_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_task_permission_error(monkeypatch):
    task = Task(title="old title", description="old description", creator_id=1)
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_update_task = AsyncMock()
    monkeypatch.setattr(task_services.task_crud, "update_task", mock_update_task)
    task_id = 1
    task_data = TaskUpdate(title="new title", description="new description")
    current_user = User(id=2)
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskPermissionError):
        await task_services.update_task_or_raise(task_id, task_data, current_user, db)
    mock_update_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_task_success(monkeypatch):
    task = Task(title="test title", description="test description", creator_id=1)
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_delete_task = AsyncMock(return_value=None)
    monkeypatch.setattr(task_services.task_crud, "delete_task", mock_delete_task)
    task_id = 1
    current_user = User(id=1)
    db = AsyncMock(spec=AsyncSession)
    result = await task_services.delete_task_or_raise(task_id, current_user, db)

    assert result is None
    mock_get_task_by_id_or_raise.assert_awaited_once_with(task_id, db)
    mock_delete_task.assert_awaited_once_with(task, db)


@pytest.mark.asyncio
async def test_delete_task_not_found_error(monkeypatch):
    mock_get_task_by_id_or_raise = AsyncMock(
        side_effect=task_services.TaskNotFoundError()
    )
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_delete_task = AsyncMock(return_value=None)
    monkeypatch.setattr(task_services.task_crud, "delete_task", mock_delete_task)
    task_id = 1
    current_user = User(id=1)
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskNotFoundError):
        await task_services.delete_task_or_raise(task_id, current_user, db)
    mock_get_task_by_id_or_raise.assert_awaited_once_with(task_id, db)
    mock_delete_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_task_permission_error(monkeypatch):
    task = Task(creator_id=2)
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_delete_task = AsyncMock(return_value=None)
    monkeypatch.setattr(task_services.task_crud, "delete_task", mock_delete_task)
    task_id = 1
    current_user = User(id=1)
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskPermissionError):
        await task_services.delete_task_or_raise(task_id, current_user, db)
    mock_get_task_by_id_or_raise.assert_awaited_once_with(task_id, db)
    mock_delete_task.assert_not_awaited()
