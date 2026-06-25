from datetime import UTC, datetime
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app
from app.models.tasks import Task, TaskStatus
from app.models.users import User
from app.services import tasks as task_services

client = TestClient(app)


def test_create_task_success(monkeypatch):
    task = Task(
        id=1,
        title="test title",
        description="test description",
        status=TaskStatus.OPEN,
        creator_id=1,
        assignee_id=2,
        created_at=datetime.now(UTC),
        team_id=2,
    )

    async def fake_get_current_user():
        return User(id=1)

    mock_create_task = AsyncMock(return_value=task)

    monkeypatch.setattr(task_services, "create_task", mock_create_task)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "test title",
                "description": "test description",
                "assignee_id": 2,
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert data["title"] == "test title"
    assert data["status"] == "open"
    assert data["description"] == "test description"
    assert data["creator_id"] == 1
    mock_create_task.assert_awaited_once()

    await_args = mock_create_task.await_args
    assert await_args is not None
    task_data, current_user, db = await_args.args
    assert current_user.id == 1
    assert task_data.title == "test title"
    assert task_data.assignee_id == 2


def test_create_task_permission_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=1)

    mock_create_task = AsyncMock(side_effect=task_services.TaskPermissionError())

    monkeypatch.setattr(task_services, "create_task", mock_create_task)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "test title",
                "description": "test description",
                "assignee_id": 2,
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert data["detail"] == "Not enough permissions"
    mock_create_task.assert_awaited_once()

    await_args = mock_create_task.await_args
    assert await_args is not None
    task_data, current_user, db = await_args.args
    assert current_user.id == 1
    assert task_data.title == "test title"
    assert task_data.assignee_id == 2


def test_create_task_user_not_in_team_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=1)

    mock_create_task = AsyncMock(side_effect=task_services.UserNotInTeamError())

    monkeypatch.setattr(task_services, "create_task", mock_create_task)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "test title",
                "description": "test description",
                "assignee_id": 2,
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert data["detail"] == "User is not in a team"
    mock_create_task.assert_awaited_once()

    await_args = mock_create_task.await_args
    assert await_args is not None
    task_data, current_user, db = await_args.args
    assert current_user.id == 1
    assert task_data.title == "test title"
    assert task_data.assignee_id == 2


def test_create_task_assignee_not_found_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=1)

    mock_create_task = AsyncMock(side_effect=task_services.TaskAssigneeNotFoundError())

    monkeypatch.setattr(task_services, "create_task", mock_create_task)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "test title",
                "description": "test description",
                "assignee_id": 2,
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert data["detail"] == "User not found"
    mock_create_task.assert_awaited_once()

    await_args = mock_create_task.await_args
    assert await_args is not None
    task_data, current_user, db = await_args.args
    assert current_user.id == 1
    assert task_data.title == "test title"
    assert task_data.assignee_id == 2


def test_create_task_team_mismatch_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=1)

    mock_create_task = AsyncMock(
        side_effect=task_services.TaskAssigneeTeamMismatchError()
    )

    monkeypatch.setattr(task_services, "create_task", mock_create_task)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "test title",
                "description": "test description",
                "assignee_id": 2,
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert data["detail"] == "Creator and assignee must be in one team"
    mock_create_task.assert_awaited_once()

    await_args = mock_create_task.await_args
    assert await_args is not None
    task_data, current_user, db = await_args.args
    assert current_user.id == 1
    assert task_data.title == "test title"
    assert task_data.assignee_id == 2


def test_get_task_by_id_success(monkeypatch):
    task = Task(
        id=1,
        title="test title",
        description="test description",
        status=TaskStatus.OPEN,
        creator_id=1,
        assignee_id=2,
        created_at=datetime.now(UTC),
        team_id=2,
    )

    async def fake_get_current_user():
        return User(id=1)

    mock_get_task_by_id_for_user_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.get("/api/v1/tasks/1")
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["title"] == "test title"
    assert data["description"] == "test description"
    assert data["status"] == "open"
    assert data["creator_id"] == 1
    mock_get_task_by_id_for_user_or_raise.assert_awaited_once()
    await_args = mock_get_task_by_id_for_user_or_raise.await_args
    assert await_args is not None
    task_id, current_user, db = await_args.args
    assert task_id == 1
    assert current_user.id == 1


def test_get_task_by_id_not_found(monkeypatch):
    mock_get_task_by_id_for_user_or_raise = AsyncMock(
        side_effect=task_services.TaskNotFoundError()
    )
    monkeypatch.setattr(
        task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )

    async def fake_get_current_user():
        return User(id=1)

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.get("/api/v1/tasks/1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_get_user_tasks(monkeypatch):
    tasks = [
        Task(
            id=1,
            title="test title",
            description="test description",
            status=TaskStatus.OPEN,
            creator_id=1,
            assignee_id=2,
            created_at=datetime.now(UTC),
            team_id=2,
        ),
        Task(
            id=2,
            title="test title2",
            description="test description2",
            status=TaskStatus.OPEN,
            creator_id=3,
            assignee_id=1,
            created_at=datetime.now(UTC),
            team_id=2,
        ),
    ]

    async def fake_get_current_user():
        return User(id=1)

    app.dependency_overrides[get_current_user] = fake_get_current_user
    mock_get_tasks_for_user = AsyncMock(return_value=tasks)
    monkeypatch.setattr(task_services, "get_tasks_for_user", mock_get_tasks_for_user)
    try:
        response = client.get("/api/v1/tasks")
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[1]["id"] == 2
    assert data[1]["title"] == "test title2"
    assert data[1]["description"] == "test description2"
    mock_get_tasks_for_user.assert_awaited_once()
    await_args = mock_get_tasks_for_user.await_args
    assert await_args is not None
    current_user, db = await_args.args
    assert current_user.id == 1


def test_update_task_success(monkeypatch):
    task = Task(
        id=1,
        title="new title",
        description="new description",
        status=TaskStatus.OPEN,
        creator_id=1,
        assignee_id=2,
        created_at=datetime.now(UTC),
        team_id=2,
    )
    mock_update_task_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services, "update_task_or_raise", mock_update_task_or_raise
    )

    async def fake_get_current_user():
        return User(id=1)

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.patch("/api/v1/tasks/1", json={"title": "new title"})
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert data["title"] == "new title"
    mock_update_task_or_raise.assert_awaited_once()
    await_args = mock_update_task_or_raise.await_args
    assert await_args is not None
    task_id, task_data, current_user, db = await_args.args
    assert task_id == 1
    assert task_data.title == "new title"
    assert current_user.id == 1


def test_update_task_not_found(monkeypatch):
    mock_update_task_or_raise = AsyncMock(side_effect=task_services.TaskNotFoundError())
    monkeypatch.setattr(
        task_services, "update_task_or_raise", mock_update_task_or_raise
    )

    async def fake_get_current_user():
        return User(id=1)

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.patch("/api/v1/tasks/1", json={"title": "new title"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
    mock_update_task_or_raise.assert_awaited_once()
    await_args = mock_update_task_or_raise.await_args
    assert await_args is not None
    task_id, task_data, current_user, db = await_args.args
    assert task_id == 1
    assert task_data.title == "new title"
    assert current_user.id == 1


def test_update_task_permission_error(monkeypatch):
    mock_update_task_or_raise = AsyncMock(
        side_effect=task_services.TaskPermissionError()
    )
    monkeypatch.setattr(
        task_services, "update_task_or_raise", mock_update_task_or_raise
    )

    async def fake_get_current_user():
        return User(id=1)

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.patch("/api/v1/tasks/1", json={"title": "new title"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"
    mock_update_task_or_raise.assert_awaited_once()
    await_args = mock_update_task_or_raise.await_args
    assert await_args is not None
    task_id, task_data, current_user, db = await_args.args
    assert task_id == 1
    assert task_data.title == "new title"
    assert current_user.id == 1


def test_delete_task_success(monkeypatch):
    mock_delete_task_or_raise = AsyncMock(return_value=None)
    monkeypatch.setattr(
        task_services, "delete_task_or_raise", mock_delete_task_or_raise
    )

    async def fake_get_current_user():
        return User(id=1)

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.delete("/api/v1/tasks/1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 204
    mock_delete_task_or_raise.assert_awaited_once()
    await_args = mock_delete_task_or_raise.await_args
    assert await_args is not None
    task_id, current_user, db = await_args.args
    assert task_id == 1
    assert current_user.id == 1


def test_delete_task_not_found_error(monkeypatch):
    mock_delete_task_or_raise = AsyncMock(side_effect=task_services.TaskNotFoundError())
    monkeypatch.setattr(
        task_services, "delete_task_or_raise", mock_delete_task_or_raise
    )

    async def fake_get_current_user():
        return User(id=1)

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.delete("/api/v1/tasks/1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
    mock_delete_task_or_raise.assert_awaited_once()
    await_args = mock_delete_task_or_raise.await_args
    assert await_args is not None
    task_id, current_user, db = await_args.args
    assert task_id == 1
    assert current_user.id == 1


def test_delete_task_permission_error(monkeypatch):
    mock_delete_task_or_raise = AsyncMock(
        side_effect=task_services.TaskPermissionError()
    )
    monkeypatch.setattr(
        task_services, "delete_task_or_raise", mock_delete_task_or_raise
    )

    async def fake_get_current_user():
        return User(id=1)

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.delete("/api/v1/tasks/1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"
    mock_delete_task_or_raise.assert_awaited_once()
    await_args = mock_delete_task_or_raise.await_args
    assert await_args is not None
    task_id, current_user, db = await_args.args
    assert task_id == 1
    assert current_user.id == 1
