from datetime import UTC, datetime

import pytest

from app.crud import comments as comment_crud
from app.models.comments import Comment
from app.models.tasks import Task
from app.models.teams import Team
from app.models.users import User
from app.schemas.comments import CommentCreate


@pytest.mark.asyncio
async def test_create_comment(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    author = User(email="1@example.com", hashed_password="hashed", team=team)
    async_session.add_all([author, team])
    await async_session.commit()
    await async_session.refresh(author)
    task = Task(
        title="Task 1",
        description="Description 1",
        creator_id=author.id,
        team_id=team.id,
    )
    async_session.add(task)
    await async_session.commit()
    await async_session.refresh(task)
    comment_data = CommentCreate(text="test comment")

    comment = await comment_crud.create_comment(
        task.id,
        author.id,
        comment_data,
        async_session,
    )

    assert comment.text == "test comment"
    assert comment.author_id == author.id
    assert comment.task_id == task.id


@pytest.mark.asyncio
async def test_get_task_comments(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    author = User(email="1@example.com", hashed_password="hashed", team=team)
    async_session.add_all([author, team])
    await async_session.commit()
    await async_session.refresh(author)
    tasks = [
        Task(
            title="Task 1",
            description="Description 1",
            creator_id=author.id,
            team_id=team.id,
        ),
        Task(
            title="Task 2",
            description="Description 2",
            creator_id=author.id,
            team_id=team.id,
        ),
    ]
    async_session.add_all(tasks)
    await async_session.commit()
    comments = [
        Comment(
            text="Comment 1",
            author_id=author.id,
            task_id=tasks[0].id,
        ),
        Comment(
            text="Comment 2",
            author_id=author.id,
            task_id=tasks[1].id,
        ),
        Comment(
            text="Comment 3",
            author_id=author.id,
            task_id=tasks[0].id,
        ),
    ]
    async_session.add_all(comments)
    await async_session.commit()

    result = await comment_crud.get_task_comments(tasks[0].id, async_session)
    result_texts = {comment.text for comment in result}

    assert author.id is not None
    assert result_texts == {"Comment 1", "Comment 3"}
    assert len(result) == 2
