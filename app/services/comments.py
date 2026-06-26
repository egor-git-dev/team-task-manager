from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import comments as comment_crud
from app.models.comments import Comment
from app.models.users import User
from app.schemas.comments import CommentCreate
from app.services import tasks as task_services


async def create_comment(
    task_id: int,
    comment_data: CommentCreate,
    current_user: User,
    db: AsyncSession,
) -> Comment:
    task = await task_services.get_task_by_id_for_user_or_raise(
        task_id, current_user, db
    )
    return await comment_crud.create_comment(task.id, current_user.id, comment_data, db)


async def get_task_comments_for_user_or_raise(
    task_id: int,
    current_user: User,
    db: AsyncSession,
) -> list[Comment]:
    task = await task_services.get_task_by_id_for_user_or_raise(
        task_id, current_user, db
    )
    return await comment_crud.get_task_comments(task.id, db)
