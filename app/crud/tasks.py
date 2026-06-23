from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tasks import Task
from app.schemas.tasks import TaskCreate


async def create_task(task_data: TaskCreate, creator_id: int, db: AsyncSession) -> Task:
    task = Task(
        title=task_data.title,
        description=task_data.description,
        deadline=task_data.deadline,
        creator_id=creator_id,
        assignee_id=task_data.assignee_id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task


async def get_task_by_id(task_id: int, db: AsyncSession) -> Task | None:
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)

    return result.scalar_one_or_none()


async def get_user_tasks(user_id: int, db: AsyncSession) -> list[Task]:
    query = (
        select(Task)
        .where(or_(Task.creator_id == user_id, Task.assignee_id == user_id))
        .order_by(Task.created_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())
