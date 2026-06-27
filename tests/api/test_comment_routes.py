from datetime import UTC, datetime
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app
from app.models.comments import Comment
from app.models.users import User
from app.services import comments as comment_services
from app.services import tasks as task_services

client = TestClient(app)


def test_create_comment_success(monkeypatch):
    comment = Comment(
        id=1,
        text="test comment",
        author_id=5,
        task_id=3,
        created_at=datetime.now(UTC),
    )

    async def fake_get_current_user():
        return User(id=5)

    mock_create_comment = AsyncMock(return_value=comment)

    monkeypatch.setattr(comment_services, "create_comment", mock_create_comment)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/tasks/3/comments",
            json={
                "text": "test comment",
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert data["text"] == "test comment"
    assert data["author_id"] == 5
    mock_create_comment.assert_awaited_once()

    await_args = mock_create_comment.await_args
    assert await_args is not None
    task_id, comment_data, current_user, db = await_args.args
    assert task_id == 3
    assert comment_data.text == "test comment"
    assert current_user.id == 5


def test_create_comment_task_not_found_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=5)

    mock_create_comment = AsyncMock(side_effect=task_services.TaskNotFoundError())

    monkeypatch.setattr(comment_services, "create_comment", mock_create_comment)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/tasks/3/comments",
            json={
                "text": "test comment",
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert data["detail"] == "Task not found"
    mock_create_comment.assert_awaited_once()

    await_args = mock_create_comment.await_args
    assert await_args is not None
    task_id, comment_data, current_user, db = await_args.args
    assert task_id == 3
    assert comment_data.text == "test comment"
    assert current_user.id == 5


def test_get_task_comments_success(monkeypatch):
    async def fake_get_current_user():
        return User(id=5)

    comments = [
        Comment(
            id=1,
            text="Comment 1",
            author_id=1,
            task_id=3,
            created_at=datetime.now(UTC),
        ),
        Comment(
            id=2,
            text="Comment 2",
            author_id=1,
            task_id=3,
            created_at=datetime.now(UTC),
        ),
        Comment(
            id=3,
            text="Comment 3",
            author_id=2,
            task_id=3,
            created_at=datetime.now(UTC),
        ),
    ]
    mock_get_task_comments_for_user_or_raise = AsyncMock(return_value=comments)
    monkeypatch.setattr(
        comment_services,
        "get_task_comments_for_user_or_raise",
        mock_get_task_comments_for_user_or_raise,
    )
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.get("/api/v1/tasks/3/comments")
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(data) == 3
    assert data[0]["text"] == "Comment 1"
    assert data[1]["task_id"] == 3
    assert data[2]["author_id"] == 2
    mock_get_task_comments_for_user_or_raise.assert_awaited_once()
    await_args = mock_get_task_comments_for_user_or_raise.await_args
    assert await_args is not None
    task_id, current_user, db = await_args.args
    assert task_id == 3
    assert current_user.id == 5


def test_get_task_comments_task_not_found_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=5)

    mock_get_task_comments_for_user_or_raise = AsyncMock(
        side_effect=task_services.TaskNotFoundError()
    )
    monkeypatch.setattr(
        comment_services,
        "get_task_comments_for_user_or_raise",
        mock_get_task_comments_for_user_or_raise,
    )
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.get("/api/v1/tasks/3/comments")
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert data["detail"] == "Task not found"

    mock_get_task_comments_for_user_or_raise.assert_awaited_once()
    await_args = mock_get_task_comments_for_user_or_raise.await_args
    assert await_args is not None
    task_id, current_user, db = await_args.args
    assert task_id == 3
    assert current_user.id == 5


def test_delete_comment_success(monkeypatch):
    async def fake_get_current_user():
        return User(id=5)

    mock_delete_comment_or_raise = AsyncMock(return_value=None)
    monkeypatch.setattr(
        comment_services,
        "delete_comment_or_raise",
        mock_delete_comment_or_raise,
    )
    app.dependency_overrides[get_current_user] = fake_get_current_user

    try:
        response = client.delete("/api/v1/tasks/5/comments/2")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 204
    mock_delete_comment_or_raise.assert_awaited_once()
    await_args = mock_delete_comment_or_raise.await_args
    assert await_args is not None
    task_id, comment_id, current_user, db = await_args.args
    assert task_id == 5
    assert comment_id == 2
    assert current_user.id == 5


def test_delete_comment_task_not_found(monkeypatch):
    async def fake_get_current_user():
        return User(id=5)

    mock_delete_comment_or_raise = AsyncMock(
        side_effect=task_services.TaskNotFoundError()
    )
    monkeypatch.setattr(
        comment_services,
        "delete_comment_or_raise",
        mock_delete_comment_or_raise,
    )
    app.dependency_overrides[get_current_user] = fake_get_current_user

    try:
        response = client.delete("/api/v1/tasks/5/comments/2")
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert data["detail"] == "Task not found"
    await_args = mock_delete_comment_or_raise.await_args
    assert await_args is not None
    task_id, comment_id, current_user, db = await_args.args
    assert task_id == 5
    assert comment_id == 2
    assert current_user.id == 5


def test_delete_comment_not_found(monkeypatch):
    async def fake_get_current_user():
        return User(id=5)

    mock_delete_comment_or_raise = AsyncMock(
        side_effect=comment_services.CommentNotFoundError()
    )
    monkeypatch.setattr(
        comment_services,
        "delete_comment_or_raise",
        mock_delete_comment_or_raise,
    )
    app.dependency_overrides[get_current_user] = fake_get_current_user

    try:
        response = client.delete("/api/v1/tasks/5/comments/2")
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert data["detail"] == "Comment not found"
    await_args = mock_delete_comment_or_raise.await_args
    assert await_args is not None
    task_id, comment_id, current_user, db = await_args.args
    assert task_id == 5
    assert comment_id == 2
    assert current_user.id == 5


def test_delete_comment_permission_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=5)

    mock_delete_comment_or_raise = AsyncMock(
        side_effect=comment_services.CommentPermissionError()
    )
    monkeypatch.setattr(
        comment_services,
        "delete_comment_or_raise",
        mock_delete_comment_or_raise,
    )
    app.dependency_overrides[get_current_user] = fake_get_current_user

    try:
        response = client.delete("/api/v1/tasks/5/comments/2")
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert data["detail"] == "Not enough permissions"
    await_args = mock_delete_comment_or_raise.await_args
    assert await_args is not None
    task_id, comment_id, current_user, db = await_args.args
    assert task_id == 5
    assert comment_id == 2
    assert current_user.id == 5
