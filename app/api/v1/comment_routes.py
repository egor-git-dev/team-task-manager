from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.comments import Comment
from app.models.users import User
from app.schemas.comments import CommentCreate, CommentRead
from app.services import comments as comment_services
from app.services import tasks as task_services

router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["Comments"])


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    task_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Comment:
    try:
        return await comment_services.create_comment(
            task_id, comment_data, current_user, db
        )
    except task_services.TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )


@router.get("", response_model=list[CommentRead], status_code=status.HTTP_200_OK)
async def get_task_comments(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Comment]:
    try:
        return await comment_services.get_task_comments_for_user_or_raise(
            task_id, current_user, db
        )
    except task_services.TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
