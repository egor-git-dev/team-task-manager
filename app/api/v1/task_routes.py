from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.tasks import Task
from app.models.users import User
from app.schemas.tasks import TaskCreate, TaskRead, TaskUpdate
from app.services import tasks as task_services

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Task:
    try:
        return await task_services.create_task(task_data, current_user, db)
    except task_services.TaskPermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    except task_services.UserNotInTeamError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is not in a team",
        )
    except task_services.TaskAssigneeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    except task_services.TaskAssigneeTeamMismatchError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Creator and assignee must be in one team",
        )


@router.get("", response_model=list[TaskRead], status_code=status.HTTP_200_OK)
async def get_user_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Task]:
    return await task_services.get_user_tasks(current_user.id, db)


@router.get("/{task_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def get_task_by_id(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Task:
    try:
        return await task_services.get_task_by_id_for_user_or_raise(
            task_id,
            current_user,
            db,
        )
    except task_services.TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )


@router.patch("/{task_id}", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Task:
    try:
        return await task_services.update_task_or_raise(
            task_id, task_data, current_user, db
        )
    except task_services.TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    except task_services.TaskPermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await task_services.delete_task_or_raise(task_id, current_user, db)
    except task_services.TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    except task_services.TaskPermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
