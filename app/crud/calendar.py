from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meetings import Meeting
from app.models.tasks import Task


async def get_user_calendar_tasks(
    user_id: int,
    starts_at: datetime,
    ends_at: datetime,
    db: AsyncSession,
) -> list[Task]:
    # Используем полуоткрытый интервал [starts_at, ends_at),
    # чтобы события на границе не попадали сразу в два периода.
    query = (
        select(Task)
        .where(
            or_(Task.creator_id == user_id, Task.assignee_id == user_id),
            Task.deadline.is_not(None),
            Task.deadline >= starts_at,
            Task.deadline < ends_at,
        )
        .order_by(Task.deadline)
    )
    result = await db.execute(query)

    return list(result.scalars().all())


async def get_team_calendar_tasks(
    team_id: int,
    starts_at: datetime,
    ends_at: datetime,
    db: AsyncSession,
) -> list[Task]:
    query = (
        select(Task)
        .where(
            Task.team_id == team_id,
            Task.deadline.is_not(None),
            Task.deadline >= starts_at,
            Task.deadline < ends_at,
        )
        .order_by(Task.deadline)
    )
    result = await db.execute(query)

    return list(result.scalars().all())


async def get_user_calendar_meetings(
    user_id: int,
    starts_at: datetime,
    ends_at: datetime,
    db: AsyncSession,
) -> list[Meeting]:
    query = (
        select(Meeting)
        .where(
            or_(Meeting.creator_id == user_id, Meeting.participant_id == user_id),
            Meeting.is_cancelled.is_(False),
            Meeting.starts_at < ends_at,
            Meeting.ends_at > starts_at,
        )
        .order_by(Meeting.starts_at)
    )
    result = await db.execute(query)

    return list(result.scalars().all())
