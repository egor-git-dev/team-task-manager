from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import tasks as task_crud
from app.models.tasks import Task
from app.schemas.tasks import TaskCreate


class TaskNotFoundError(Exception):
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
