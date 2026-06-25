from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import tasks as task_crud
from app.crud import users as user_crud
from app.models.tasks import Task
from app.models.users import User, UserRole
from app.schemas.tasks import TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    pass


class TaskPermissionError(Exception):
    pass


class TaskAssigneeTeamMismatchError(Exception):
    pass


class TaskAssigneeNotFoundError(Exception):
    pass


class UserNotInTeamError(Exception):
    pass


async def get_task_by_id_or_raise(task_id: int, db: AsyncSession) -> Task:
    task = await task_crud.get_task_by_id(task_id, db)
    if task is None:
        raise TaskNotFoundError()
    return task


async def get_task_by_id_for_user_or_raise(
    task_id: int, current_user: User, db: AsyncSession
) -> Task:
    task = await task_crud.get_task_by_id(task_id, db)
    if task is None:
        raise TaskNotFoundError()
    if current_user.team_id != task.team_id:
        raise TaskNotFoundError()
    if current_user.id == task.creator_id or current_user.id == task.assignee_id:
        return task
    if current_user.role in {UserRole.MANAGER, UserRole.ADMIN}:
        return task

    raise TaskNotFoundError()


async def create_task(
    task_data: TaskCreate,
    current_user: User,
    db: AsyncSession,
) -> Task:
    if current_user.role not in {UserRole.ADMIN, UserRole.MANAGER}:
        raise TaskPermissionError()
    if current_user.team_id is None:
        raise UserNotInTeamError()
    if task_data.assignee_id is not None:
        assignee = await user_crud.get_user_by_id(task_data.assignee_id, db)
        if assignee is None:
            raise TaskAssigneeNotFoundError()
        if current_user.team_id != assignee.team_id:
            raise TaskAssigneeTeamMismatchError()
    return await task_crud.create_task(
        task_data,
        current_user.id,
        current_user.team_id,
        db,
    )


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
