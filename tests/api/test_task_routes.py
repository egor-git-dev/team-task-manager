from datetime import UTC, datetime
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app
from app.models.tasks import Task, TaskStatus
from app.models.users import User
from app.services import tasks as task_services

client = TestClient(app)


def test_create_task(monkeypatch):
    task = Task(
        id=1,
        title="test title",
        description="test description",
        status=TaskStatus.OPEN,
        creator_id=1,
        assignee_id=2,
        created_at=datetime.now(UTC),
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
    task_data, creator_id, db = await_args.args
    assert creator_id == 1
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
    )

    async def fake_get_current_user():
        return User(id=1)

    mock_get_task_by_id_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        task_services,
        "get_task_by_id_or_raise",
        mock_get_task_by_id_or_raise,
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
    mock_get_task_by_id_or_raise.assert_awaited_once()
    await_args = mock_get_task_by_id_or_raise.await_args
    assert await_args is not None
    task_id, db = await_args.args
    assert task_id == 1


def test_get_task_by_id_not_found(monkeypatch):
    mock_get_task_by_id_or_raise = AsyncMock(
        side_effect=task_services.TaskNotFoundError()
    )
    monkeypatch.setattr(
        task_services, "get_task_by_id_or_raise", mock_get_task_by_id_or_raise
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
