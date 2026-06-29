from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.meetings import Meeting
from app.models.tasks import Task
from app.models.users import User
from app.schemas.calendar import CalendarRead
from app.services import calendar as calendar_services

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get("", response_model=CalendarRead, status_code=status.HTTP_200_OK)
async def get_calendar(
    starts_at: datetime,
    ends_at: datetime,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, list[Task] | list[Meeting]]:
    if ends_at <= starts_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date range",
        )
    return await calendar_services.get_calendar(current_user, starts_at, ends_at, db)
