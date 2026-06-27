from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comments import Comment
from app.schemas.comments import CommentCreate


async def create_comment(
    task_id: int,
    author_id: int,
    comment_data: CommentCreate,
    db: AsyncSession,
) -> Comment:
    comment = Comment(
        task_id=task_id,
        author_id=author_id,
        text=comment_data.text,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return comment


async def get_task_comments(task_id: int, db: AsyncSession) -> list[Comment]:
    query = (
        select(Comment)
        .where(Comment.task_id == task_id)
        .order_by(Comment.created_at.desc())
    )
    result = await db.execute(query)

    return list(result.scalars().all())


async def get_comment_by_id(comment_id: int, db: AsyncSession) -> Comment | None:
    query = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def delete_comment(comment: Comment, db: AsyncSession) -> None:
    await db.delete(comment)
    await db.commit()
