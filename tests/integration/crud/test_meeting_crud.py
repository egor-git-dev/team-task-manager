from datetime import UTC, datetime, timedelta

import pytest

from app.crud import meetings as meeting_crud
from app.models.teams import Team
from app.models.users import User
from app.schemas.meetings import MeetingCreate


@pytest.mark.asyncio
async def test_create_meeting(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    participant = User(
        email="testuser@example.com",
        hashed_password="hashed",
        team=team,
    )
    creator = User(
        email="creatoruser@example.com",
        hashed_password="hashed",
        team=team,
    )
    async_session.add_all([participant, creator, team])
    await async_session.commit()
    await async_session.refresh(participant)
    await async_session.refresh(creator)
    starts_at = datetime.now(UTC)
    ends_at = starts_at + timedelta(hours=1)
    meeting_data = MeetingCreate(
        title="Test Meeting",
        description="This is a test meeting.",
        starts_at=starts_at,
        ends_at=ends_at,
        participant_id=participant.id,
    )

    meeting = await meeting_crud.create_meeting(
        meeting_data, creator.id, team.id, async_session
    )

    assert meeting.title == "Test Meeting"
    assert meeting.description == "This is a test meeting."
    assert meeting.creator_id == creator.id
    assert meeting.participant_id == participant.id


@pytest.mark.asyncio
async def test_get_meeting_by_id(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    participant = User(
        email="testuser@example.com",
        hashed_password="hashed",
        team=team,
    )
    creator = User(
        email="creatoruser@example.com",
        hashed_password="hashed",
        team=team,
    )
    async_session.add_all([team, participant, creator])
    await async_session.commit()
    await async_session.refresh(participant)
    await async_session.refresh(creator)
    await async_session.refresh(team)

    starts_at = datetime.now(UTC)
    ends_at = starts_at + timedelta(hours=1)

    meeting_data = MeetingCreate(
        title="Test Meeting",
        description="This is a test meeting.",
        starts_at=starts_at,
        ends_at=ends_at,
        participant_id=participant.id,
    )
    created_meeting = await meeting_crud.create_meeting(
        meeting_data,
        creator.id,
        team.id,
        async_session,
    )

    meeting = await meeting_crud.get_meeting_by_id(
        created_meeting.id,
        async_session,
    )

    assert meeting is not None
    assert meeting.id == created_meeting.id
    assert meeting.title == "Test Meeting"
    assert meeting.creator_id == creator.id
    assert meeting.participant_id == participant.id


@pytest.mark.asyncio
async def test_get_user_meetings(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    participant = User(
        email="testuser@example.com",
        hashed_password="hashed",
        team=team,
    )
    creator = User(
        email="creatoruser@example.com",
        hashed_password="hashed",
        team=team,
    )
    async_session.add_all([team, participant, creator])
    await async_session.commit()
    await async_session.refresh(participant)
    await async_session.refresh(creator)
    await async_session.refresh(team)

    starts_at = datetime.now(UTC)
    ends_at = starts_at + timedelta(hours=1)

    meeting_data = MeetingCreate(
        title="Test Meeting",
        description="This is a test meeting.",
        starts_at=starts_at,
        ends_at=ends_at,
        participant_id=participant.id,
    )
    created_meeting = await meeting_crud.create_meeting(
        meeting_data,
        creator.id,
        team.id,
        async_session,
    )

    creator_meetings = await meeting_crud.get_user_meetings(creator.id, async_session)
    participant_meetings = await meeting_crud.get_user_meetings(
        participant.id, async_session
    )

    assert len(creator_meetings) == 1
    assert creator_meetings[0].id == created_meeting.id
    assert creator_meetings[0].title == "Test Meeting"
    assert creator_meetings[0].creator_id == creator.id
    assert creator_meetings[0].participant_id == participant.id

    assert len(participant_meetings) == 1
    assert participant_meetings[0].id == created_meeting.id
    assert participant_meetings[0].title == "Test Meeting"
    assert participant_meetings[0].creator_id == creator.id
    assert participant_meetings[0].participant_id == participant.id


@pytest.mark.asyncio
async def test_has_time_overlap_returns_true(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    participant = User(
        email="testuser@example.com",
        hashed_password="hashed",
        team=team,
    )
    creator = User(
        email="creatoruser@example.com",
        hashed_password="hashed",
        team=team,
    )
    async_session.add_all([team, participant, creator])
    await async_session.commit()
    await async_session.refresh(participant)
    await async_session.refresh(creator)
    await async_session.refresh(team)

    starts_at = datetime.now(UTC) + timedelta(days=1)
    ends_at = starts_at + timedelta(hours=1)

    meeting_data = MeetingCreate(
        title="Test Meeting",
        description="This is a test meeting.",
        starts_at=starts_at,
        ends_at=ends_at,
        participant_id=participant.id,
    )
    await meeting_crud.create_meeting(
        meeting_data,
        creator.id,
        team.id,
        async_session,
    )

    has_overlap = await meeting_crud.has_time_overlap(
        participant.id,
        starts_at + timedelta(minutes=30),
        ends_at + timedelta(minutes=30),
        async_session,
    )

    assert has_overlap is True


@pytest.mark.asyncio
async def test_has_time_overlap_returns_false_for_adjacent_meeting(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    participant = User(
        email="testuser@example.com",
        hashed_password="hashed",
        team=team,
    )
    creator = User(
        email="creatoruser@example.com",
        hashed_password="hashed",
        team=team,
    )
    async_session.add_all([team, participant, creator])
    await async_session.commit()
    await async_session.refresh(participant)
    await async_session.refresh(creator)
    await async_session.refresh(team)

    starts_at = datetime.now(UTC) + timedelta(days=1)
    ends_at = starts_at + timedelta(hours=1)

    meeting_data = MeetingCreate(
        title="Test Meeting",
        description="This is a test meeting.",
        starts_at=starts_at,
        ends_at=ends_at,
        participant_id=participant.id,
    )
    await meeting_crud.create_meeting(
        meeting_data,
        creator.id,
        team.id,
        async_session,
    )

    has_overlap = await meeting_crud.has_time_overlap(
        participant.id,
        ends_at,
        ends_at + timedelta(hours=1),
        async_session,
    )

    assert has_overlap is False


@pytest.mark.asyncio
async def test_cancel_meeting(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    participant = User(
        email="testuser@example.com",
        hashed_password="hashed",
        team=team,
    )
    creator = User(
        email="creatoruser@example.com",
        hashed_password="hashed",
        team=team,
    )
    async_session.add_all([team, participant, creator])
    await async_session.commit()
    await async_session.refresh(participant)
    await async_session.refresh(creator)
    await async_session.refresh(team)

    starts_at = datetime.now(UTC) + timedelta(days=1)
    ends_at = starts_at + timedelta(hours=1)

    meeting_data = MeetingCreate(
        title="Test Meeting",
        description="This is a test meeting.",
        starts_at=starts_at,
        ends_at=ends_at,
        participant_id=participant.id,
    )
    meeting = await meeting_crud.create_meeting(
        meeting_data,
        creator.id,
        team.id,
        async_session,
    )

    cancelled_meeting = await meeting_crud.cancel_meeting(meeting, async_session)

    assert cancelled_meeting.id == meeting.id
    assert cancelled_meeting.is_cancelled is True


@pytest.mark.asyncio
async def test_has_time_overlap_ignores_cancelled_meeting(async_session):
    team = Team(name="test team", join_code="TEST1234", created_at=datetime.now(UTC))
    participant = User(
        email="testuser@example.com",
        hashed_password="hashed",
        team=team,
    )
    creator = User(
        email="creatoruser@example.com",
        hashed_password="hashed",
        team=team,
    )
    async_session.add_all([team, participant, creator])
    await async_session.commit()
    await async_session.refresh(participant)
    await async_session.refresh(creator)
    await async_session.refresh(team)

    starts_at = datetime.now(UTC) + timedelta(days=1)
    ends_at = starts_at + timedelta(hours=1)

    meeting_data = MeetingCreate(
        title="Test Meeting",
        description="This is a test meeting.",
        starts_at=starts_at,
        ends_at=ends_at,
        participant_id=participant.id,
    )
    meeting = await meeting_crud.create_meeting(
        meeting_data,
        creator.id,
        team.id,
        async_session,
    )
    await meeting_crud.cancel_meeting(meeting, async_session)

    has_overlap = await meeting_crud.has_time_overlap(
        participant.id,
        starts_at + timedelta(minutes=30),
        ends_at + timedelta(minutes=30),
        async_session,
    )

    assert has_overlap is False
