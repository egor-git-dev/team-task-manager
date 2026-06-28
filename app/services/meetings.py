from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import meetings as meeting_crud
from app.crud import users as user_crud
from app.models.meetings import Meeting
from app.models.users import User, UserRole
from app.schemas.meetings import MeetingCreate


class MeetingPermissionError(Exception):
    pass


class UserNotInTeamError(Exception):
    pass


class MeetingParticipantNotFoundError(Exception):
    pass


class MeetingParticipantTeamMismatchError(Exception):
    pass


class MeetingSelfBookingError(Exception):
    pass


class MeetingTimeOverlapError(Exception):
    pass


class MeetingNotFoundError(Exception):
    pass


async def create_meeting(
    meeting_data: MeetingCreate,
    current_user: User,
    db: AsyncSession,
) -> Meeting:
    if current_user.role not in {UserRole.MANAGER, UserRole.ADMIN}:
        raise MeetingPermissionError()
    if current_user.team_id is None:
        raise UserNotInTeamError()
    participant = await user_crud.get_user_by_id(meeting_data.participant_id, db)
    if participant is None:
        raise MeetingParticipantNotFoundError()
    if participant.team_id != current_user.team_id:
        raise MeetingParticipantTeamMismatchError()
    if current_user.id == participant.id:
        raise MeetingSelfBookingError()
    if await meeting_crud.has_time_overlap(
        participant.id, meeting_data.starts_at, meeting_data.ends_at, db
    ):
        raise MeetingTimeOverlapError()
    if await meeting_crud.has_time_overlap(
        current_user.id,
        meeting_data.starts_at,
        meeting_data.ends_at,
        db,
    ):
        raise MeetingTimeOverlapError()
    return await meeting_crud.create_meeting(
        meeting_data,
        current_user.id,
        current_user.team_id,
        db,
    )


async def get_current_user_meetings(
    current_user: User,
    db: AsyncSession,
) -> list[Meeting]:
    return await meeting_crud.get_user_meetings(current_user.id, db)


async def cancel_meeting(
    meeting_id: int, current_user: User, db: AsyncSession
) -> Meeting:
    meeting = await meeting_crud.get_meeting_by_id(meeting_id, db)
    if meeting is None:
        raise MeetingNotFoundError()
    if current_user.team_id != meeting.team_id:
        raise MeetingNotFoundError()
    if meeting.is_cancelled:
        return meeting
    if current_user.id == meeting.creator_id:
        return await meeting_crud.cancel_meeting(meeting, db)
    if current_user.role in {UserRole.MANAGER, UserRole.ADMIN}:
        return await meeting_crud.cancel_meeting(meeting, db)
    raise MeetingPermissionError()
