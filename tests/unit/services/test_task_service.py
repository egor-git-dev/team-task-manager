from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tasks import Task, TaskStatus
from app.models.users import User, UserRole
from app.schemas.tasks import TaskCreate, TaskUpdate
from app.services import tasks as task_services


@pytest.mark.asyncio
async def test_create_task_without_assignee_by_manager(monkeypatch):
    task = Task(title="test_title", description="test_description")
    mock_create_task = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "create_task", mock_create_task)
    mock_get_user_by_id = AsyncMock(return_value=None)
    monkeypatch.setattr(task_services.user_crud, "get_user_by_id", mock_get_user_by_id)
    db = AsyncMock(spec=AsyncSession)
    task_data = TaskCreate(
        title="test_title",
        description="test_description",
    )
    user = User(id=1, role=UserRole.MANAGER, team_id=2)
    team_id = 2

    result = await task_services.create_task(task_data, user, db)

    assert result is task
    mock_create_task.assert_awaited_once_with(task_data, user.id, team_id, db)
    mock_get_user_by_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_task_without_assignee_by_admin(monkeypatch):
    task = Task(title="test_title", description="test_description")
    mock_create_task = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "create_task", mock_create_task)
    mock_get_user_by_id = AsyncMock(return_value=None)
    monkeypatch.setattr(task_services.user_crud, "get_user_by_id", mock_get_user_by_id)
    db = AsyncMock(spec=AsyncSession)
    task_data = TaskCreate(
        title="test_title",
        description="test_description",
    )
    user = User(id=1, role=UserRole.ADMIN, team_id=2)
    team_id = 2

    result = await task_services.create_task(task_data, user, db)

    assert result is task
    mock_create_task.assert_awaited_once_with(task_data, user.id, team_id, db)
    mock_get_user_by_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_task_with_same_team_assignee(monkeypatch):
    task = Task(title="test_title", description="test_description")
    mock_create_task = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "create_task", mock_create_task)
    assignee = User(team_id=2)
    mock_get_user_by_id = AsyncMock(return_value=assignee)
    monkeypatch.setattr(task_services.user_crud, "get_user_by_id", mock_get_user_by_id)
    db = AsyncMock(spec=AsyncSession)
    task_data = TaskCreate(
        title="test_title",
        description="test_description",
        assignee_id=2,
    )
    user = User(id=1, role=UserRole.MANAGER, team_id=2)
    team_id = 2

    result = await task_services.create_task(task_data, user, db)

    assert result is task
    mock_create_task.assert_awaited_once_with(task_data, user.id, team_id, db)
    mock_get_user_by_id.assert_awaited_once_with(2, db)


@pytest.mark.asyncio
async def test_create_task_by_user_error(monkeypatch):
    mock_create_task = AsyncMock()
    monkeypatch.setattr(task_services.task_crud, "create_task", mock_create_task)
    mock_get_user_by_id = AsyncMock()
    monkeypatch.setattr(task_services.user_crud, "get_user_by_id", mock_get_user_by_id)
    db = AsyncMock(spec=AsyncSession)
    task_data = TaskCreate(
        title="test_title",
        description="test_description",
        assignee_id=2,
    )
    user = User(id=1, role=UserRole.USER, team_id=2)

    with pytest.raises(task_services.TaskPermissionError):
        await task_services.create_task(task_data, user, db)
    mock_get_user_by_id.assert_not_awaited()
    mock_create_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_task_by_manager_not_in_team(monkeypatch):
    mock_create_task = AsyncMock()
    monkeypatch.setattr(task_services.task_crud, "create_task", mock_create_task)
    mock_get_user_by_id = AsyncMock()
    monkeypatch.setattr(task_services.user_crud, "get_user_by_id", mock_get_user_by_id)
    db = AsyncMock(spec=AsyncSession)
    task_data = TaskCreate(
        title="test_title",
        description="test_description",
        assignee_id=2,
    )
    user = User(id=1, role=UserRole.MANAGER)

    with pytest.raises(task_services.UserNotInTeamError):
        await task_services.create_task(task_data, user, db)
    mock_get_user_by_id.assert_not_awaited()
    mock_create_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_task_assignee_not_found_error(monkeypatch):
    mock_create_task = AsyncMock()
    monkeypatch.setattr(task_services.task_crud, "create_task", mock_create_task)
    mock_get_user_by_id = AsyncMock(return_value=None)
    monkeypatch.setattr(task_services.user_crud, "get_user_by_id", mock_get_user_by_id)
    db = AsyncMock(spec=AsyncSession)
    task_data = TaskCreate(
        title="test_title",
        description="test_description",
        assignee_id=2,
    )
    user = User(id=1, role=UserRole.MANAGER, team_id=2)

    with pytest.raises(task_services.TaskAssigneeNotFoundError):
        await task_services.create_task(task_data, user, db)
    mock_get_user_by_id.assert_awaited_once_with(task_data.assignee_id, db)
    mock_create_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_task_assignee_from_another_team(monkeypatch):
    mock_create_task = AsyncMock()
    monkeypatch.setattr(task_services.task_crud, "create_task", mock_create_task)
    assignee = User(team_id=3)
    mock_get_user_by_id = AsyncMock(return_value=assignee)
    monkeypatch.setattr(task_services.user_crud, "get_user_by_id", mock_get_user_by_id)
    db = AsyncMock(spec=AsyncSession)
    task_data = TaskCreate(
        title="test_title",
        description="test_description",
        assignee_id=2,
    )
    user = User(id=1, role=UserRole.MANAGER, team_id=2)

    with pytest.raises(task_services.TaskAssigneeTeamMismatchError):
        await task_services.create_task(task_data, user, db)
    mock_get_user_by_id.assert_awaited_once_with(task_data.assignee_id, db)
    mock_create_task.assert_not_awaited()


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
    task = Task(
        title="old title",
        description="old description",
        creator_id=1,
        team_id=3,
    )
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_update_task = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "update_task", mock_update_task)
    task_id = 1
    task_data = TaskUpdate(title="new title", description="new description")
    current_user = User(id=1, team_id=3)
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
    task = Task(
        title="old title",
        description="old description",
        creator_id=1,
        assignee_id=2,
        team_id=2,
    )
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_update_task = AsyncMock()
    monkeypatch.setattr(task_services.task_crud, "update_task", mock_update_task)
    task_id = 1
    task_data = TaskUpdate(title="new title", status=TaskStatus.IN_PROGRESS)
    current_user = User(id=2, team_id=2, role=UserRole.USER)
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskPermissionError):
        await task_services.update_task_or_raise(task_id, task_data, current_user, db)
    mock_update_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_task_by_manager_success(monkeypatch):
    task = Task(
        title="old title",
        description="old description",
        creator_id=1,
        team_id=3,
    )
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_update_task = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "update_task", mock_update_task)
    task_id = 1
    task_data = TaskUpdate(title="new title", description="new description")
    current_user = User(id=5, team_id=3, role=UserRole.MANAGER)
    db = AsyncMock(spec=AsyncSession)
    result = await task_services.update_task_or_raise(
        task_id, task_data, current_user, db
    )

    assert result is task
    mock_get_task_by_id_or_raise.assert_awaited_once_with(task_id, db)
    mock_update_task.assert_awaited_once_with(task, task_data, db)


@pytest.mark.asyncio
async def test_update_task_status_by_assignee_success(monkeypatch):
    task = Task(
        title="old title",
        description="old description",
        creator_id=1,
        assignee_id=4,
        team_id=3,
    )
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_update_task = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "update_task", mock_update_task)
    task_id = 1
    task_data = TaskUpdate(status=TaskStatus.IN_PROGRESS)
    current_user = User(id=4, team_id=3, role=UserRole.USER)
    db = AsyncMock(spec=AsyncSession)
    result = await task_services.update_task_or_raise(
        task_id, task_data, current_user, db
    )

    assert result is task
    mock_get_task_by_id_or_raise.assert_awaited_once_with(task_id, db)
    mock_update_task.assert_awaited_once_with(task, task_data, db)


@pytest.mark.asyncio
async def test_update_task_by_unrelated_team_user_not_found(monkeypatch):
    task = Task(
        title="old title",
        description="old description",
        creator_id=1,
        assignee_id=4,
        team_id=3,
    )
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_update_task = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "update_task", mock_update_task)
    task_id = 1
    task_data = TaskUpdate(status=TaskStatus.IN_PROGRESS)
    current_user = User(id=9, team_id=3, role=UserRole.USER)
    db = AsyncMock(spec=AsyncSession)
    with pytest.raises(task_services.TaskNotFoundError):
        await task_services.update_task_or_raise(task_id, task_data, current_user, db)

    mock_get_task_by_id_or_raise.assert_awaited_once_with(task_id, db)
    mock_update_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_task_by_other_team_user_not_found(monkeypatch):
    task = Task(
        title="old title",
        description="old description",
        creator_id=1,
        assignee_id=4,
        team_id=3,
    )
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_update_task = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "update_task", mock_update_task)
    task_id = 1
    task_data = TaskUpdate(status=TaskStatus.IN_PROGRESS)
    current_user = User(id=9, team_id=5, role=UserRole.USER)
    db = AsyncMock(spec=AsyncSession)
    with pytest.raises(task_services.TaskNotFoundError):
        await task_services.update_task_or_raise(task_id, task_data, current_user, db)

    mock_get_task_by_id_or_raise.assert_awaited_once_with(task_id, db)
    mock_update_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_task_by_creator_success(monkeypatch):
    task = Task(title="test title", creator_id=1, team_id=3)
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_delete_task = AsyncMock(return_value=None)
    monkeypatch.setattr(task_services.task_crud, "delete_task", mock_delete_task)
    task_id = 1
    current_user = User(id=1, team_id=3, role=UserRole.USER)
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
async def test_delete_task_by_assignee_permission_error(monkeypatch):
    task = Task(creator_id=2, assignee_id=1, team_id=3)
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_delete_task = AsyncMock(return_value=None)
    monkeypatch.setattr(task_services.task_crud, "delete_task", mock_delete_task)
    task_id = 1
    current_user = User(id=1, team_id=3, role=UserRole.USER)
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskPermissionError):
        await task_services.delete_task_or_raise(task_id, current_user, db)
    mock_get_task_by_id_or_raise.assert_awaited_once_with(task_id, db)
    mock_delete_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_task_by_other_team_user_not_found(monkeypatch):
    task = Task(creator_id=2, assignee_id=1, team_id=3)
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_delete_task = AsyncMock(return_value=None)
    monkeypatch.setattr(task_services.task_crud, "delete_task", mock_delete_task)
    task_id = 1
    current_user = User(id=1, team_id=5, role=UserRole.USER)
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskNotFoundError):
        await task_services.delete_task_or_raise(task_id, current_user, db)
    mock_get_task_by_id_or_raise.assert_awaited_once_with(task_id, db)
    mock_delete_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_task_by_unrelated_team_user_not_found(monkeypatch):
    task = Task(creator_id=2, team_id=3, assignee_id=7)
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_delete_task = AsyncMock(return_value=None)
    monkeypatch.setattr(task_services.task_crud, "delete_task", mock_delete_task)
    task_id = 1
    current_user = User(id=1, team_id=3, role=UserRole.USER)
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskNotFoundError):
        await task_services.delete_task_or_raise(task_id, current_user, db)
    mock_get_task_by_id_or_raise.assert_awaited_once_with(task_id, db)
    mock_delete_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_task_by_manager_success(monkeypatch):
    task = Task(title="test title", creator_id=1, team_id=3)
    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
    )
    mock_delete_task = AsyncMock(return_value=None)
    monkeypatch.setattr(task_services.task_crud, "delete_task", mock_delete_task)
    task_id = 1
    current_user = User(id=2, team_id=3, role=UserRole.MANAGER)
    db = AsyncMock(spec=AsyncSession)
    result = await task_services.delete_task_or_raise(task_id, current_user, db)

    assert result is None
    mock_get_task_by_id_or_raise.assert_awaited_once_with(task_id, db)
    mock_delete_task.assert_awaited_once_with(task, db)


@pytest.mark.asyncio
async def test_get_task_by_id_for_user_or_raise_creator_get_task(monkeypatch):
    task = Task(
        title="test_title",
        description="test_description",
        creator_id=2,
        team_id=3,
    )
    mock_get_task_by_id = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "get_task_by_id", mock_get_task_by_id)
    current_user = User(id=2, team_id=3, role=UserRole.USER)
    task_id = 1
    db = AsyncMock(spec=AsyncSession)

    result = await task_services.get_task_by_id_for_user_or_raise(
        task_id,
        current_user,
        db,
    )

    assert result is task
    mock_get_task_by_id.assert_awaited_once_with(task_id, db)


@pytest.mark.asyncio
async def test_get_task_by_id_for_user_or_raise_assignee_get_task(monkeypatch):
    task = Task(
        title="test_title",
        description="test_description",
        creator_id=2,
        assignee_id=1,
        team_id=3,
    )
    mock_get_task_by_id = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "get_task_by_id", mock_get_task_by_id)
    current_user = User(id=1, team_id=3, role=UserRole.USER)
    task_id = 1
    db = AsyncMock(spec=AsyncSession)

    result = await task_services.get_task_by_id_for_user_or_raise(
        task_id,
        current_user,
        db,
    )

    assert result is task
    mock_get_task_by_id.assert_awaited_once_with(task_id, db)


@pytest.mark.asyncio
async def test_get_task_by_id_for_user_or_raise_user_from_another_team_error(
    monkeypatch,
):
    task = Task(
        title="test_title",
        description="test_description",
        creator_id=2,
        team_id=3,
    )
    mock_get_task_by_id = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "get_task_by_id", mock_get_task_by_id)
    current_user = User(id=1, team_id=2, role=UserRole.USER)
    task_id = 1
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskNotFoundError):
        await task_services.get_task_by_id_for_user_or_raise(
            task_id,
            current_user,
            db,
        )

    mock_get_task_by_id.assert_awaited_once_with(task_id, db)


@pytest.mark.asyncio
async def test_get_task_by_id_for_user_or_raise_manager_get_task(monkeypatch):
    task = Task(
        title="test_title",
        description="test_description",
        team_id=3,
    )
    mock_get_task_by_id = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "get_task_by_id", mock_get_task_by_id)
    current_user = User(team_id=3, role=UserRole.MANAGER)
    task_id = 1
    db = AsyncMock(spec=AsyncSession)

    result = await task_services.get_task_by_id_for_user_or_raise(
        task_id,
        current_user,
        db,
    )

    assert result is task
    mock_get_task_by_id.assert_awaited_once_with(task_id, db)


@pytest.mark.asyncio
async def test_get_task_by_id_for_user_or_raise_team_user_without_relation_error(
    monkeypatch,
):
    task = Task(
        title="test_title",
        description="test_description",
        creator_id=2,
        team_id=3,
    )
    mock_get_task_by_id = AsyncMock(return_value=task)
    monkeypatch.setattr(task_services.task_crud, "get_task_by_id", mock_get_task_by_id)
    current_user = User(id=5, team_id=3, role=UserRole.USER)
    task_id = 1
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskNotFoundError):
        await task_services.get_task_by_id_for_user_or_raise(
            task_id,
            current_user,
            db,
        )

    mock_get_task_by_id.assert_awaited_once_with(task_id, db)


@pytest.mark.asyncio
async def test_get_task_by_id_for_user_or_raise_task_not_found(monkeypatch):
    mock_get_task_by_id = AsyncMock(return_value=None)
    monkeypatch.setattr(task_services.task_crud, "get_task_by_id", mock_get_task_by_id)
    current_user = User(id=2, team_id=3, role=UserRole.USER)
    task_id = 1
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskNotFoundError):
        await task_services.get_task_by_id_for_user_or_raise(
            task_id,
            current_user,
            db,
        )

    mock_get_task_by_id.assert_awaited_once_with(task_id, db)


@pytest.mark.asyncio
async def test_get_tasks_for_user_manager_with_team(monkeypatch):
    tasks = [
        Task(title="test_title", description="test_description"),
        Task(title="test_title2", description="test_description2"),
    ]
    mock_get_user_tasks = AsyncMock()
    monkeypatch.setattr(task_services.task_crud, "get_user_tasks", mock_get_user_tasks)
    mock_get_team_tasks = AsyncMock(return_value=tasks)
    monkeypatch.setattr(task_services.task_crud, "get_team_tasks", mock_get_team_tasks)
    db = AsyncMock(spec=AsyncSession)
    current_user = User(team_id=2, role=UserRole.MANAGER)

    result = await task_services.get_tasks_for_user(current_user, db)

    assert result is tasks
    mock_get_team_tasks.assert_awaited_once_with(current_user.team_id, db)
    mock_get_user_tasks.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_tasks_for_user_admin_without_team(monkeypatch):
    tasks = [
        Task(title="test_title", description="test_description"),
        Task(title="test_title2", description="test_description2"),
    ]
    mock_get_user_tasks = AsyncMock()
    monkeypatch.setattr(task_services.task_crud, "get_user_tasks", mock_get_user_tasks)
    mock_get_team_tasks = AsyncMock(return_value=tasks)
    monkeypatch.setattr(task_services.task_crud, "get_team_tasks", mock_get_team_tasks)
    db = AsyncMock(spec=AsyncSession)
    current_user = User(role=UserRole.ADMIN)

    result = await task_services.get_tasks_for_user(current_user, db)

    assert result == []
    mock_get_user_tasks.assert_not_awaited()
    mock_get_team_tasks.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_tasks_for_user_regular_user_with_team(monkeypatch):
    tasks = [
        Task(title="test_title", description="test_description"),
        Task(title="test_title2", description="test_description2"),
    ]
    mock_get_user_tasks = AsyncMock(return_value=tasks)
    monkeypatch.setattr(task_services.task_crud, "get_user_tasks", mock_get_user_tasks)
    mock_get_team_tasks = AsyncMock()
    monkeypatch.setattr(task_services.task_crud, "get_team_tasks", mock_get_team_tasks)
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=1, team_id=2, role=UserRole.USER)

    result = await task_services.get_tasks_for_user(current_user, db)

    assert result is tasks
    mock_get_user_tasks.assert_awaited_once_with(current_user.id, db)
    mock_get_team_tasks.assert_not_awaited()
