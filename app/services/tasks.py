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
    # Чужие задачи маскируем как 404: так пользователь не узнает,
    # существует ли задача в другой команде.
    if current_user.team_id != task.team_id:
        raise TaskNotFoundError()
    if current_user.id == task.creator_id or current_user.id == task.assignee_id:
        return task
    if current_user.role in {UserRole.MANAGER, UserRole.ADMIN}:
        return task

    raise TaskNotFoundError()


async def get_tasks_for_user(current_user: User, db: AsyncSession) -> list[Task]:
    if current_user.role in {UserRole.MANAGER, UserRole.ADMIN}:
        if current_user.team_id is not None:
            return await task_crud.get_team_tasks(current_user.team_id, db)
        return []
    return await task_crud.get_user_tasks(current_user.id, db)


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
    update_data = task_data.model_dump(exclude_unset=True)
    update_fields = set(update_data)
    if current_user.team_id != task.team_id:
        raise TaskNotFoundError()
    # Если меняем исполнителя, проверяем его отдельно:
    # задача не должна перейти пользователю из другой команды.
    if "assignee_id" in update_data and update_data["assignee_id"] is not None:
        assignee = await user_crud.get_user_by_id(update_data["assignee_id"], db)
        if assignee is None:
            raise TaskAssigneeNotFoundError()
        if assignee.team_id != task.team_id:
            raise TaskAssigneeTeamMismatchError()
    if current_user.id == task.creator_id:
        return await task_crud.update_task(task, task_data, db)
    if current_user.role in {UserRole.MANAGER, UserRole.ADMIN}:
        return await task_crud.update_task(task, task_data, db)
    # Исполнитель может двигать свою задачу по статусам,
    # но не менять описание, дедлайн или назначение.
    if current_user.id == task.assignee_id:
        if update_fields <= {"status"}:
            return await task_crud.update_task(task, task_data, db)
        raise TaskPermissionError()
    raise TaskNotFoundError()


async def delete_task_or_raise(
    task_id: int, current_user: User, db: AsyncSession
) -> None:
    task = await get_task_by_id_or_raise(task_id, db)
    if current_user.team_id != task.team_id:
        raise TaskNotFoundError()
    if current_user.id == task.creator_id:
        await task_crud.delete_task(task, db)
        return
    if current_user.role in {UserRole.MANAGER, UserRole.ADMIN}:
        await task_crud.delete_task(task, db)
        return
    if current_user.id == task.assignee_id:
        raise TaskPermissionError()
    raise TaskNotFoundError()
