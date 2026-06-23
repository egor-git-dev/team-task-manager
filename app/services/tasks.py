from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import tasks as task_crud
from app.models.tasks import Task
from app.models.users import User
from app.schemas.tasks import TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    pass


class TaskPermissionError(Exception):
    pass


async def get_task_by_id_or_raise(task_id: int, db: AsyncSession) -> Task:
    task = await task_crud.get_task_by_id(task_id, db)
    if task is None:
        raise TaskNotFoundError()
    return task


async def create_task(task_data: TaskCreate, creator_id: int, db: AsyncSession) -> Task:
    return await task_crud.create_task(task_data, creator_id, db)


async def get_user_tasks(user_id: int, db: AsyncSession) -> list[Task]:
    return await task_crud.get_user_tasks(user_id, db)


async def update_task_or_raise(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User,
    db: AsyncSession,
) -> Task:
    task = await get_task_by_id_or_raise(task_id, db)
    if current_user.id != task.creator_id:
        raise TaskPermissionError()
    return await task_crud.update_task(task, task_data, db)


async def delete_task_or_raise(
    task_id: int, current_user: User, db: AsyncSession
) -> None:
    task = await get_task_by_id_or_raise(task_id, db)
    if current_user.id != task.creator_id:
        raise TaskPermissionError()
    await task_crud.delete_task(task, db)
