from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comments import Comment
from app.models.tasks import Task
from app.models.users import User, UserRole
from app.schemas.comments import CommentCreate
from app.services import comments as comment_services
from app.services import tasks as task_services


@pytest.mark.asyncio
async def test_create_comment_success(monkeypatch):
    current_user = User(id=1, team_id=2)
    task = Task(id=5, team_id=2)
    comment = Comment(id=1, text="test_comment", author_id=1, task_id=5)
    comment_data = CommentCreate(text="test comment")
    mock_get_task_by_id_for_user_or_raise = AsyncMock(return_value=task)
    mock_create_comment = AsyncMock(return_value=comment)
    monkeypatch.setattr(
        comment_services.task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    monkeypatch.setattr(
        comment_services.comment_crud,
        "create_comment",
        mock_create_comment,
    )
    db = AsyncMock(spec=AsyncSession)

    result = await comment_services.create_comment(
        task.id, comment_data, current_user, db
    )

    assert result is comment
    mock_get_task_by_id_for_user_or_raise.assert_awaited_once_with(
        task.id, current_user, db
    )
    mock_create_comment.assert_awaited_once_with(
        task.id, current_user.id, comment_data, db
    )


@pytest.mark.asyncio
async def test_create_comment_task_not_found_error(monkeypatch):
    current_user = User(id=1, team_id=2)
    task = Task(id=1, team_id=2)
    comment_data = CommentCreate(text="test comment")
    mock_get_task_by_id_for_user_or_raise = AsyncMock(
        side_effect=task_services.TaskNotFoundError()
    )
    mock_create_comment = AsyncMock()
    monkeypatch.setattr(
        comment_services.task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    monkeypatch.setattr(
        comment_services.comment_crud,
        "create_comment",
        mock_create_comment,
    )
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskNotFoundError):
        await comment_services.create_comment(task.id, comment_data, current_user, db)

    mock_get_task_by_id_for_user_or_raise.assert_awaited_once_with(
        task.id, current_user, db
    )
    mock_create_comment.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_task_comments_for_user_or_raise_success(monkeypatch):
    comments = [
        Comment(
            text="Comment 1",
            author_id=1,
        ),
        Comment(
            text="Comment 2",
            author_id=1,
        ),
        Comment(
            text="Comment 3",
            author_id=2,
        ),
    ]
    task = Task(id=4)
    current_user = User(id=2)
    mock_get_task_by_id_for_user_or_raise = AsyncMock(return_value=task)
    monkeypatch.setattr(
        comment_services.task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    mock_get_task_comments = AsyncMock(return_value=comments)
    monkeypatch.setattr(
        comment_services.comment_crud,
        "get_task_comments",
        mock_get_task_comments,
    )
    db = AsyncMock(spec=AsyncSession)

    result = await comment_services.get_task_comments_for_user_or_raise(
        task.id, current_user, db
    )
    result_texts = {comment.text for comment in result}

    assert result is comments
    assert result_texts == {"Comment 1", "Comment 2", "Comment 3"}
    mock_get_task_by_id_for_user_or_raise.assert_awaited_once_with(
        task.id, current_user, db
    )
    mock_get_task_comments.assert_awaited_once_with(task.id, db)


@pytest.mark.asyncio
async def test_get_task_comments_for_user_or_raise_task_not_found_error(monkeypatch):
    current_user = User(id=2)
    mock_get_task_by_id_for_user_or_raise = AsyncMock(
        side_effect=task_services.TaskNotFoundError()
    )
    task_id = 4
    monkeypatch.setattr(
        comment_services.task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    mock_get_task_comments = AsyncMock()
    monkeypatch.setattr(
        comment_services.comment_crud,
        "get_task_comments",
        mock_get_task_comments,
    )
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(task_services.TaskNotFoundError):
        await comment_services.get_task_comments_for_user_or_raise(
            task_id, current_user, db
        )

    mock_get_task_by_id_for_user_or_raise.assert_awaited_once_with(
        task_id, current_user, db
    )
    mock_get_task_comments.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_comment_by_id_or_raise_success(monkeypatch):
    task = Task(id=3)
    comment = Comment(id=1, text="test comment", task_id=3)
    mock_get_task_by_id_for_user_or_raise = AsyncMock(return_value=task)
    mock_get_comment_by_id = AsyncMock(return_value=comment)
    monkeypatch.setattr(
        comment_services.task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    monkeypatch.setattr(
        comment_services.comment_crud,
        "get_comment_by_id",
        mock_get_comment_by_id,
    )
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=1, team_id=3, role=UserRole.MANAGER)

    result = await comment_services.get_comment_by_id_or_raise(
        task.id, comment.id, current_user, db
    )

    assert result is comment
    mock_get_task_by_id_for_user_or_raise.assert_awaited_once_with(
        task.id, current_user, db
    )
    mock_get_comment_by_id.assert_awaited_once_with(comment.id, db)


@pytest.mark.asyncio
async def test_get_comment_by_id_or_raise_comment_not_found(monkeypatch):
    task = Task(id=3)
    comment = Comment(id=1, text="test comment", task_id=3)
    mock_get_task_by_id_for_user_or_raise = AsyncMock(return_value=task)
    mock_get_comment_by_id = AsyncMock(return_value=None)
    monkeypatch.setattr(
        comment_services.task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    monkeypatch.setattr(
        comment_services.comment_crud,
        "get_comment_by_id",
        mock_get_comment_by_id,
    )
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=1, team_id=3, role=UserRole.MANAGER)

    with pytest.raises(comment_services.CommentNotFoundError):
        await comment_services.get_comment_by_id_or_raise(
            task.id, comment.id, current_user, db
        )

    mock_get_task_by_id_for_user_or_raise.assert_awaited_once_with(
        task.id, current_user, db
    )
    mock_get_comment_by_id.assert_awaited_once_with(comment.id, db)


@pytest.mark.asyncio
async def test_get_comment_by_id_or_raise_comment_belongs_to_another_task(monkeypatch):
    task = Task(id=5)
    comment = Comment(id=1, text="test comment", task_id=3)
    mock_get_task_by_id_for_user_or_raise = AsyncMock(return_value=task)
    mock_get_comment_by_id = AsyncMock(return_value=comment)
    monkeypatch.setattr(
        comment_services.task_services,
        "get_task_by_id_for_user_or_raise",
        mock_get_task_by_id_for_user_or_raise,
    )
    monkeypatch.setattr(
        comment_services.comment_crud,
        "get_comment_by_id",
        mock_get_comment_by_id,
    )
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=1, team_id=3, role=UserRole.MANAGER)

    with pytest.raises(comment_services.CommentNotFoundError):
        await comment_services.get_comment_by_id_or_raise(
            task.id, comment.id, current_user, db
        )

    mock_get_task_by_id_for_user_or_raise.assert_awaited_once_with(
        task.id, current_user, db
    )
    mock_get_comment_by_id.assert_awaited_once_with(comment.id, db)


@pytest.mark.asyncio
async def test_delete_comment_or_raise_success(monkeypatch):
    task = Task(id=5)
    comment = Comment(id=1, text="test comment", task_id=5, author_id=3)
    mock_get_comment_by_id_or_raise = AsyncMock(return_value=comment)
    mock_delete_comment = AsyncMock(return_value=None)
    monkeypatch.setattr(
        comment_services,
        "get_comment_by_id_or_raise",
        mock_get_comment_by_id_or_raise,
    )
    monkeypatch.setattr(
        comment_services.comment_crud,
        "delete_comment",
        mock_delete_comment,
    )
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=3, team_id=3)

    result = await comment_services.delete_comment_or_raise(
        task.id, comment.id, current_user, db
    )

    assert result is None
    mock_get_comment_by_id_or_raise.assert_awaited_once_with(
        task.id, comment.id, current_user, db
    )
    mock_delete_comment.assert_awaited_once_with(comment, db)


@pytest.mark.asyncio
async def test_delete_comment_or_raise_success_by_manager(monkeypatch):
    task = Task(id=5)
    comment = Comment(id=1, text="test comment", task_id=5, author_id=2)
    mock_get_comment_by_id_or_raise = AsyncMock(return_value=comment)
    mock_delete_comment = AsyncMock(return_value=None)
    monkeypatch.setattr(
        comment_services,
        "get_comment_by_id_or_raise",
        mock_get_comment_by_id_or_raise,
    )
    monkeypatch.setattr(
        comment_services.comment_crud,
        "delete_comment",
        mock_delete_comment,
    )
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=3, team_id=3, role=UserRole.MANAGER)

    result = await comment_services.delete_comment_or_raise(
        task.id, comment.id, current_user, db
    )

    assert result is None
    mock_get_comment_by_id_or_raise.assert_awaited_once_with(
        task.id, comment.id, current_user, db
    )
    mock_delete_comment.assert_awaited_once_with(comment, db)


@pytest.mark.asyncio
async def test_delete_comment_or_raise_not_author_permission_error(monkeypatch):
    task = Task(id=5)
    comment = Comment(id=1, text="test comment", task_id=5, author_id=2)
    mock_get_comment_by_id_or_raise = AsyncMock(return_value=comment)
    mock_delete_comment = AsyncMock()
    monkeypatch.setattr(
        comment_services,
        "get_comment_by_id_or_raise",
        mock_get_comment_by_id_or_raise,
    )
    monkeypatch.setattr(
        comment_services.comment_crud,
        "delete_comment",
        mock_delete_comment,
    )
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=3, team_id=3, role=UserRole.USER)

    with pytest.raises(comment_services.CommentPermissionError):
        await comment_services.delete_comment_or_raise(
            task.id, comment.id, current_user, db
        )

    mock_get_comment_by_id_or_raise.assert_awaited_once_with(
        task.id, comment.id, current_user, db
    )
    mock_delete_comment.assert_not_awaited()
