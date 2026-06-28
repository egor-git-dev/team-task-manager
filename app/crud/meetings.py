from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meetings import Meeting
from app.schemas.meetings import MeetingCreate


async def create_meeting(
    meeting_data: MeetingCreate,
    creator_id: int,
    team_id: int,
    db: AsyncSession,
) -> Meeting:
    meeting = Meeting(
        title=meeting_data.title,
        description=meeting_data.description,
        starts_at=meeting_data.starts_at,
        ends_at=meeting_data.ends_at,
        creator_id=creator_id,
        participant_id=meeting_data.participant_id,
        team_id=team_id,
    )
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)

    return meeting


async def get_meeting_by_id(meeting_id: int, db: AsyncSession) -> Meeting | None:
    query = select(Meeting).where(Meeting.id == meeting_id)
    result = await db.execute(query)

    return result.scalar_one_or_none()


async def get_user_meetings(user_id: int, db: AsyncSession) -> list[Meeting]:
    query = (
        select(Meeting)
        .where(
            or_(
                Meeting.creator_id == user_id,
                Meeting.participant_id == user_id,
            )
        )
        .order_by(Meeting.starts_at)
    )
    result = await db.execute(query)

    return list(result.scalars().all())


async def has_time_overlap(
    participant_id: int,
    starts_at: datetime,
    ends_at: datetime,
    db: AsyncSession,
) -> bool:
    query = select(Meeting).where(
        Meeting.participant_id == participant_id,
        Meeting.is_cancelled.is_(False),
        Meeting.starts_at < ends_at,
        Meeting.ends_at > starts_at,
    )
    result = await db.execute(query)

    return result.scalar_one_or_none() is not None


async def cancel_meeting(meeting: Meeting, db: AsyncSession) -> Meeting:
    meeting.is_cancelled = True
    await db.commit()
    await db.refresh(meeting)
    return meeting
