from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import calendar as calendar_crud
from app.models.meetings import Meeting
from app.models.tasks import Task
from app.models.users import User, UserRole


async def get_calendar(
    current_user: User,
    starts_at: datetime,
    ends_at: datetime,
    db: AsyncSession,
) -> dict[str, list[Task] | list[Meeting]]:
    if (
        current_user.role in {UserRole.MANAGER, UserRole.ADMIN}
        and current_user.team_id is not None
    ):
        tasks = await calendar_crud.get_team_calendar_tasks(
            current_user.team_id, starts_at, ends_at, db
        )
    else:
        tasks = await calendar_crud.get_user_calendar_tasks(
            current_user.id, starts_at, ends_at, db
        )
    meetings = await calendar_crud.get_user_calendar_meetings(
        current_user.id, starts_at, ends_at, db
    )
    return {"tasks": tasks, "meetings": meetings}
