from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, call

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meetings import Meeting
from app.models.users import User, UserRole
from app.schemas.meetings import MeetingCreate
from app.services import meetings as meeting_services


@pytest.mark.asyncio
async def test_create_meeting_success(monkeypatch):
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=1, team_id=5, role=UserRole.ADMIN)
    participant = User(id=2, team_id=5)
    starts_at = datetime.now(UTC)
    meeting_data = MeetingCreate(
        title="test meeting",
        description="test description",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
        participant_id=participant.id,
    )
    meeting = Meeting(
        id=1,
        title="test meeting",
        description="test descrtiption",
        participant_id=participant.id,
    )
    mock_get_user_by_id = AsyncMock(return_value=participant)
    mock_has_time_overlap = AsyncMock(return_value=False)
    mock_create_meeting = AsyncMock(return_value=meeting)
    monkeypatch.setattr(
        meeting_services.user_crud, "get_user_by_id", mock_get_user_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "has_time_overlap", mock_has_time_overlap
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "create_meeting", mock_create_meeting
    )

    result = await meeting_services.create_meeting(meeting_data, current_user, db)

    assert result is meeting
    mock_get_user_by_id.assert_awaited_once_with(participant.id, db)
    mock_has_time_overlap.assert_has_awaits(
        [
            call(participant.id, meeting_data.starts_at, meeting_data.ends_at, db),
            call(current_user.id, meeting_data.starts_at, meeting_data.ends_at, db),
        ]
    )
    mock_create_meeting.assert_awaited_once_with(
        meeting_data, current_user.id, current_user.team_id, db
    )


@pytest.mark.asyncio
async def test_create_meeting_permission_error(monkeypatch):
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=1, team_id=5, role=UserRole.USER)
    participant = User(id=2, team_id=5)
    starts_at = datetime.now(UTC)
    meeting_data = MeetingCreate(
        title="test meeting",
        description="test description",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
        participant_id=participant.id,
    )
    meeting = Meeting(
        id=1,
        title="test meeting",
        description="test descrtiption",
        participant_id=participant.id,
    )
    mock_get_user_by_id = AsyncMock(return_value=participant)
    mock_has_time_overlap = AsyncMock(return_value=False)
    mock_create_meeting = AsyncMock(return_value=meeting)
    monkeypatch.setattr(
        meeting_services.user_crud, "get_user_by_id", mock_get_user_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "has_time_overlap", mock_has_time_overlap
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "create_meeting", mock_create_meeting
    )

    with pytest.raises(meeting_services.MeetingPermissionError):
        await meeting_services.create_meeting(meeting_data, current_user, db)

    mock_get_user_by_id.assert_not_awaited()
    mock_has_time_overlap.assert_not_awaited()
    mock_create_meeting.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_meeting_user_not_in_team(monkeypatch):
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=1, team_id=None, role=UserRole.ADMIN)
    participant = User(id=2, team_id=5)
    starts_at = datetime.now(UTC)
    meeting_data = MeetingCreate(
        title="test meeting",
        description="test description",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
        participant_id=participant.id,
    )
    meeting = Meeting(
        id=1,
        title="test meeting",
        description="test descrtiption",
        participant_id=participant.id,
    )
    mock_get_user_by_id = AsyncMock(return_value=participant)
    mock_has_time_overlap = AsyncMock(return_value=False)
    mock_create_meeting = AsyncMock(return_value=meeting)
    monkeypatch.setattr(
        meeting_services.user_crud, "get_user_by_id", mock_get_user_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "has_time_overlap", mock_has_time_overlap
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "create_meeting", mock_create_meeting
    )

    with pytest.raises(meeting_services.UserNotInTeamError):
        await meeting_services.create_meeting(meeting_data, current_user, db)

    mock_get_user_by_id.assert_not_awaited()
    mock_has_time_overlap.assert_not_awaited()
    mock_create_meeting.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_meeting_participant_not_found(monkeypatch):
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=1, team_id=5, role=UserRole.ADMIN)
    participant = User(id=2, team_id=5)
    starts_at = datetime.now(UTC)
    meeting_data = MeetingCreate(
        title="test meeting",
        description="test description",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
        participant_id=participant.id,
    )
    meeting = Meeting(
        id=1,
        title="test meeting",
        description="test descrtiption",
        participant_id=participant.id,
    )
    mock_get_user_by_id = AsyncMock(return_value=None)
    mock_has_time_overlap = AsyncMock(return_value=False)
    mock_create_meeting = AsyncMock(return_value=meeting)
    monkeypatch.setattr(
        meeting_services.user_crud, "get_user_by_id", mock_get_user_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "has_time_overlap", mock_has_time_overlap
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "create_meeting", mock_create_meeting
    )

    with pytest.raises(meeting_services.MeetingParticipantNotFoundError):
        await meeting_services.create_meeting(meeting_data, current_user, db)

    mock_get_user_by_id.assert_awaited_once_with(participant.id, db)
    mock_has_time_overlap.assert_not_awaited()
    mock_create_meeting.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_meeting_participant_team_mismatch(monkeypatch):
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=1, team_id=3, role=UserRole.ADMIN)
    participant = User(id=2, team_id=5)
    starts_at = datetime.now(UTC)
    meeting_data = MeetingCreate(
        title="test meeting",
        description="test description",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
        participant_id=participant.id,
    )
    meeting = Meeting(
        id=1,
        title="test meeting",
        description="test descrtiption",
        participant_id=participant.id,
    )
    mock_get_user_by_id = AsyncMock(return_value=participant)
    mock_has_time_overlap = AsyncMock(return_value=False)
    mock_create_meeting = AsyncMock(return_value=meeting)
    monkeypatch.setattr(
        meeting_services.user_crud, "get_user_by_id", mock_get_user_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "has_time_overlap", mock_has_time_overlap
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "create_meeting", mock_create_meeting
    )

    with pytest.raises(meeting_services.MeetingParticipantTeamMismatchError):
        await meeting_services.create_meeting(meeting_data, current_user, db)

    mock_get_user_by_id.assert_awaited_once_with(participant.id, db)
    mock_has_time_overlap.assert_not_awaited()
    mock_create_meeting.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_meeting_self_booking(monkeypatch):
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=1, team_id=5, role=UserRole.ADMIN)
    participant = User(id=1, team_id=5)
    starts_at = datetime.now(UTC)
    meeting_data = MeetingCreate(
        title="test meeting",
        description="test description",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
        participant_id=participant.id,
    )
    meeting = Meeting(
        id=1,
        title="test meeting",
        description="test descrtiption",
        participant_id=participant.id,
    )
    mock_get_user_by_id = AsyncMock(return_value=participant)
    mock_has_time_overlap = AsyncMock(return_value=False)
    mock_create_meeting = AsyncMock(return_value=meeting)
    monkeypatch.setattr(
        meeting_services.user_crud, "get_user_by_id", mock_get_user_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "has_time_overlap", mock_has_time_overlap
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "create_meeting", mock_create_meeting
    )

    with pytest.raises(meeting_services.MeetingSelfBookingError):
        await meeting_services.create_meeting(meeting_data, current_user, db)

    mock_get_user_by_id.assert_awaited_once_with(participant.id, db)
    mock_has_time_overlap.assert_not_awaited()
    mock_create_meeting.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_meeting_participant_time_overlap(monkeypatch):
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=1, team_id=5, role=UserRole.ADMIN)
    participant = User(id=2, team_id=5)
    starts_at = datetime.now(UTC)
    meeting_data = MeetingCreate(
        title="test meeting",
        description="test description",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
        participant_id=participant.id,
    )
    meeting = Meeting(
        id=1,
        title="test meeting",
        description="test descrtiption",
        participant_id=participant.id,
    )
    mock_get_user_by_id = AsyncMock(return_value=participant)
    mock_has_time_overlap = AsyncMock(return_value=True)
    mock_create_meeting = AsyncMock(return_value=meeting)
    monkeypatch.setattr(
        meeting_services.user_crud, "get_user_by_id", mock_get_user_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "has_time_overlap", mock_has_time_overlap
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "create_meeting", mock_create_meeting
    )

    with pytest.raises(meeting_services.MeetingTimeOverlapError):
        await meeting_services.create_meeting(meeting_data, current_user, db)

    mock_get_user_by_id.assert_awaited_once_with(participant.id, db)
    mock_has_time_overlap.assert_awaited_once_with(
        participant.id,
        meeting_data.starts_at,
        meeting_data.ends_at,
        db,
    )
    mock_create_meeting.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_meeting_creator_time_overlap(monkeypatch):
    db = AsyncMock(spec=AsyncSession)
    current_user = User(id=1, team_id=5, role=UserRole.ADMIN)
    participant = User(id=2, team_id=5)
    starts_at = datetime.now(UTC)
    meeting_data = MeetingCreate(
        title="test meeting",
        description="test description",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
        participant_id=participant.id,
    )
    meeting = Meeting(
        id=1,
        title="test meeting",
        description="test descrtiption",
        participant_id=participant.id,
    )
    mock_get_user_by_id = AsyncMock(return_value=participant)
    mock_has_time_overlap = AsyncMock(side_effect=[False, True])
    mock_create_meeting = AsyncMock(return_value=meeting)
    monkeypatch.setattr(
        meeting_services.user_crud, "get_user_by_id", mock_get_user_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "has_time_overlap", mock_has_time_overlap
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "create_meeting", mock_create_meeting
    )

    with pytest.raises(meeting_services.MeetingTimeOverlapError):
        await meeting_services.create_meeting(meeting_data, current_user, db)

    mock_get_user_by_id.assert_awaited_once_with(participant.id, db)
    mock_has_time_overlap.assert_has_awaits(
        [
            call(participant.id, meeting_data.starts_at, meeting_data.ends_at, db),
            call(current_user.id, meeting_data.starts_at, meeting_data.ends_at, db),
        ]
    )
    mock_create_meeting.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_current_user_meetings(monkeypatch):
    current_user = User(id=1)
    db = AsyncMock(spec=AsyncSession)
    meetings = [
        Meeting(id=1, title="first meeting", creator_id=1),
        Meeting(id=2, title="second meeting", participant_id=1),
    ]
    mock_get_user_meetings = AsyncMock(return_value=meetings)
    monkeypatch.setattr(
        meeting_services.meeting_crud, "get_user_meetings", mock_get_user_meetings
    )

    result = await meeting_services.get_current_user_meetings(current_user, db)
    meetings_titles = {meeting.title for meeting in result}

    assert result is meetings
    assert meetings_titles == {"first meeting", "second meeting"}
    mock_get_user_meetings.assert_awaited_once_with(current_user.id, db)


@pytest.mark.asyncio
async def test_cancel_meeting_success_by_creator(monkeypatch):
    current_user = User(id=1, role=UserRole.USER, team_id=3)
    meeting = Meeting(
        id=1, title="first meeting", creator_id=1, team_id=3, is_cancelled=False
    )
    meeting_cancelled = Meeting(
        id=1, title="first meeting", creator_id=1, is_cancelled=True
    )
    db = AsyncMock(spec=AsyncSession)
    mock_get_meeting_by_id = AsyncMock(return_value=meeting)
    mock_cancel_meeting = AsyncMock(return_value=meeting_cancelled)
    monkeypatch.setattr(
        meeting_services.meeting_crud, "get_meeting_by_id", mock_get_meeting_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "cancel_meeting", mock_cancel_meeting
    )

    result = await meeting_services.cancel_meeting(meeting.id, current_user, db)

    assert result is meeting_cancelled
    mock_get_meeting_by_id.assert_awaited_once_with(meeting.id, db)
    mock_cancel_meeting.assert_awaited_once_with(meeting, db)


@pytest.mark.asyncio
async def test_cancel_meeting_success_by_manager(monkeypatch):
    current_user = User(id=1, role=UserRole.MANAGER, team_id=3)
    meeting = Meeting(
        id=1, title="first meeting", creator_id=4, team_id=3, is_cancelled=False
    )
    meeting_cancelled = Meeting(
        id=1, title="first meeting", creator_id=1, is_cancelled=True
    )
    db = AsyncMock(spec=AsyncSession)
    mock_get_meeting_by_id = AsyncMock(return_value=meeting)
    mock_cancel_meeting = AsyncMock(return_value=meeting_cancelled)
    monkeypatch.setattr(
        meeting_services.meeting_crud, "get_meeting_by_id", mock_get_meeting_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "cancel_meeting", mock_cancel_meeting
    )

    result = await meeting_services.cancel_meeting(meeting.id, current_user, db)

    assert result is meeting_cancelled
    mock_get_meeting_by_id.assert_awaited_once_with(meeting.id, db)
    mock_cancel_meeting.assert_awaited_once_with(meeting, db)


@pytest.mark.asyncio
async def test_cancel_meeting_not_found(monkeypatch):
    current_user = User(id=1, role=UserRole.MANAGER)
    meeting = Meeting(id=1, title="first meeting", creator_id=4, is_cancelled=False)
    meeting_cancelled = Meeting(
        id=1, title="first meeting", creator_id=1, is_cancelled=True
    )
    db = AsyncMock(spec=AsyncSession)
    mock_get_meeting_by_id = AsyncMock(return_value=None)
    mock_cancel_meeting = AsyncMock(return_value=meeting_cancelled)
    monkeypatch.setattr(
        meeting_services.meeting_crud, "get_meeting_by_id", mock_get_meeting_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "cancel_meeting", mock_cancel_meeting
    )
    with pytest.raises(meeting_services.MeetingNotFoundError):
        await meeting_services.cancel_meeting(meeting.id, current_user, db)

    mock_get_meeting_by_id.assert_awaited_once_with(meeting.id, db)
    mock_cancel_meeting.assert_not_awaited()


@pytest.mark.asyncio
async def test_cancel_meeting_other_team_as_not_found(monkeypatch):
    current_user = User(id=1, role=UserRole.MANAGER, team_id=7)
    meeting = Meeting(
        id=1, title="first meeting", creator_id=4, is_cancelled=False, team_id=10
    )
    meeting_cancelled = Meeting(
        id=1, title="first meeting", creator_id=1, is_cancelled=True
    )
    db = AsyncMock(spec=AsyncSession)
    mock_get_meeting_by_id = AsyncMock(return_value=meeting)
    mock_cancel_meeting = AsyncMock(return_value=meeting_cancelled)
    monkeypatch.setattr(
        meeting_services.meeting_crud, "get_meeting_by_id", mock_get_meeting_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "cancel_meeting", mock_cancel_meeting
    )
    with pytest.raises(meeting_services.MeetingNotFoundError):
        await meeting_services.cancel_meeting(meeting.id, current_user, db)

    mock_get_meeting_by_id.assert_awaited_once_with(meeting.id, db)
    mock_cancel_meeting.assert_not_awaited()


@pytest.mark.asyncio
async def test_cancel_meeting_permission_error(monkeypatch):
    current_user = User(id=1, role=UserRole.USER, team_id=7)
    meeting = Meeting(
        id=1, title="first meeting", creator_id=4, is_cancelled=False, team_id=7
    )
    meeting_cancelled = Meeting(
        id=1, title="first meeting", creator_id=1, is_cancelled=True
    )
    db = AsyncMock(spec=AsyncSession)
    mock_get_meeting_by_id = AsyncMock(return_value=meeting)
    mock_cancel_meeting = AsyncMock(return_value=meeting_cancelled)
    monkeypatch.setattr(
        meeting_services.meeting_crud, "get_meeting_by_id", mock_get_meeting_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "cancel_meeting", mock_cancel_meeting
    )
    with pytest.raises(meeting_services.MeetingPermissionError):
        await meeting_services.cancel_meeting(meeting.id, current_user, db)

    mock_get_meeting_by_id.assert_awaited_once_with(meeting.id, db)
    mock_cancel_meeting.assert_not_awaited()


@pytest.mark.asyncio
async def test_cancel_meeting_with_cancelled_meeting(monkeypatch):
    current_user = User(id=1, role=UserRole.MANAGER, team_id=7)
    meeting = Meeting(
        id=1, title="first meeting", creator_id=4, is_cancelled=True, team_id=7
    )
    db = AsyncMock(spec=AsyncSession)
    mock_get_meeting_by_id = AsyncMock(return_value=meeting)
    mock_cancel_meeting = AsyncMock()
    monkeypatch.setattr(
        meeting_services.meeting_crud, "get_meeting_by_id", mock_get_meeting_by_id
    )
    monkeypatch.setattr(
        meeting_services.meeting_crud, "cancel_meeting", mock_cancel_meeting
    )
    result = await meeting_services.cancel_meeting(meeting.id, current_user, db)

    assert result is meeting
    mock_get_meeting_by_id.assert_awaited_once_with(meeting.id, db)
    mock_cancel_meeting.assert_not_awaited()
