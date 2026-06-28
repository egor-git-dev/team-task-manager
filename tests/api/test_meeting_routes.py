from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app
from app.models.meetings import Meeting
from app.models.users import User, UserRole
from app.services import meetings as meeting_services

client = TestClient(app)


def test_create_meeting_success(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    starts_at = datetime.now(UTC)
    meeting = Meeting(
        id=1,
        title="test meeting",
        description="test description",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
        creator_id=1,
        participant_id=5,
        team_id=7,
        is_cancelled=False,
        created_at=datetime.now(UTC),
    )
    mock_create_meeting = AsyncMock(return_value=meeting)
    monkeypatch.setattr(meeting_services, "create_meeting", mock_create_meeting)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/meetings",
            json={
                "title": "test meeting",
                "description": "test description",
                "starts_at": starts_at.isoformat(),
                "ends_at": (starts_at + timedelta(hours=1)).isoformat(),
                "participant_id": 5,
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert data["title"] == "test meeting"
    assert data["description"] == "test description"
    await_args = mock_create_meeting.await_args
    assert await_args is not None
    meeting_data, current_user, db = await_args.args
    assert meeting_data.participant_id == 5
    assert current_user.id == 2


def test_create_meeting_permission_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.USER)

    starts_at = datetime.now(UTC)
    mock_create_meeting = AsyncMock(
        side_effect=meeting_services.MeetingPermissionError()
    )
    monkeypatch.setattr(meeting_services, "create_meeting", mock_create_meeting)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/meetings",
            json={
                "title": "test meeting",
                "description": "test description",
                "starts_at": starts_at.isoformat(),
                "ends_at": (starts_at + timedelta(hours=1)).isoformat(),
                "participant_id": 5,
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert data["detail"] == "Not enough permissions"
    await_args = mock_create_meeting.await_args
    assert await_args is not None
    meeting_data, current_user, db = await_args.args
    assert meeting_data.participant_id == 5
    assert current_user.id == 2


def test_create_meeting_user_not_in_team(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    starts_at = datetime.now(UTC)
    mock_create_meeting = AsyncMock(side_effect=meeting_services.UserNotInTeamError())
    monkeypatch.setattr(meeting_services, "create_meeting", mock_create_meeting)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/meetings",
            json={
                "title": "test meeting",
                "description": "test description",
                "starts_at": starts_at.isoformat(),
                "ends_at": (starts_at + timedelta(hours=1)).isoformat(),
                "participant_id": 5,
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert data["detail"] == "User is not in a team"
    await_args = mock_create_meeting.await_args
    assert await_args is not None
    meeting_data, current_user, db = await_args.args
    assert meeting_data.participant_id == 5
    assert current_user.id == 2


def test_create_meeting_participant_not_found(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    starts_at = datetime.now(UTC)
    mock_create_meeting = AsyncMock(
        side_effect=meeting_services.MeetingParticipantNotFoundError()
    )
    monkeypatch.setattr(meeting_services, "create_meeting", mock_create_meeting)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/meetings",
            json={
                "title": "test meeting",
                "description": "test description",
                "starts_at": starts_at.isoformat(),
                "ends_at": (starts_at + timedelta(hours=1)).isoformat(),
                "participant_id": 5,
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert data["detail"] == "User not found"
    await_args = mock_create_meeting.await_args
    assert await_args is not None
    meeting_data, current_user, db = await_args.args
    assert meeting_data.participant_id == 5
    assert current_user.id == 2


def test_create_meeting_participant_team_mismatch(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    starts_at = datetime.now(UTC)
    mock_create_meeting = AsyncMock(
        side_effect=meeting_services.MeetingParticipantTeamMismatchError()
    )
    monkeypatch.setattr(meeting_services, "create_meeting", mock_create_meeting)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/meetings",
            json={
                "title": "test meeting",
                "description": "test description",
                "starts_at": starts_at.isoformat(),
                "ends_at": (starts_at + timedelta(hours=1)).isoformat(),
                "participant_id": 5,
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert data["detail"] == "Participant is in other team"
    await_args = mock_create_meeting.await_args
    assert await_args is not None
    meeting_data, current_user, db = await_args.args
    assert meeting_data.participant_id == 5
    assert current_user.id == 2


def test_create_meeting_self_booking(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    starts_at = datetime.now(UTC)
    mock_create_meeting = AsyncMock(
        side_effect=meeting_services.MeetingSelfBookingError()
    )
    monkeypatch.setattr(meeting_services, "create_meeting", mock_create_meeting)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/meetings",
            json={
                "title": "test meeting",
                "description": "test description",
                "starts_at": starts_at.isoformat(),
                "ends_at": (starts_at + timedelta(hours=1)).isoformat(),
                "participant_id": 5,
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert data["detail"] == "You cannot be participant"
    await_args = mock_create_meeting.await_args
    assert await_args is not None
    meeting_data, current_user, db = await_args.args
    assert meeting_data.participant_id == 5
    assert current_user.id == 2


def test_create_meeting_time_overlap(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    starts_at = datetime.now(UTC)
    mock_create_meeting = AsyncMock(
        side_effect=meeting_services.MeetingTimeOverlapError()
    )
    monkeypatch.setattr(meeting_services, "create_meeting", mock_create_meeting)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post(
            "/api/v1/meetings",
            json={
                "title": "test meeting",
                "description": "test description",
                "starts_at": starts_at.isoformat(),
                "ends_at": (starts_at + timedelta(hours=1)).isoformat(),
                "participant_id": 5,
            },
        )
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert data["detail"] == "Meeting time overlaps with existing meeting"
    await_args = mock_create_meeting.await_args
    assert await_args is not None
    meeting_data, current_user, db = await_args.args
    assert meeting_data.participant_id == 5
    assert current_user.id == 2


def test_get_my_meetings_success(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.USER)

    starts_at = datetime.now(UTC)
    meetings = [
        Meeting(
            id=1,
            title="first meeting",
            description="first description",
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=1),
            creator_id=2,
            participant_id=5,
            team_id=1,
            is_cancelled=False,
            created_at=datetime.now(UTC),
        ),
        Meeting(
            id=2,
            title="second meeting",
            description="second description",
            starts_at=starts_at + timedelta(days=1),
            ends_at=starts_at + timedelta(days=1, hours=1),
            creator_id=4,
            participant_id=2,
            team_id=1,
            is_cancelled=False,
            created_at=datetime.now(UTC),
        ),
    ]

    mock_get_current_user_meetings = AsyncMock(return_value=meetings)
    monkeypatch.setattr(
        meeting_services,
        "get_current_user_meetings",
        mock_get_current_user_meetings,
    )

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.get("/api/v1/meetings")
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["title"] == "first meeting"
    assert data[1]["title"] == "second meeting"

    await_args = mock_get_current_user_meetings.await_args
    assert await_args is not None
    current_user, db = await_args.args
    assert current_user.id == 2


def test_cancel_meeting_success(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    starts_at = datetime.now(UTC)
    meeting = Meeting(
        id=1,
        title="test meeting",
        description="test description",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
        creator_id=4,
        participant_id=5,
        team_id=1,
        is_cancelled=True,
        created_at=datetime.now(UTC),
    )

    mock_cancel_meeting = AsyncMock(return_value=meeting)
    monkeypatch.setattr(meeting_services, "cancel_meeting", mock_cancel_meeting)

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.patch("/api/v1/meetings/1/cancel")
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["is_cancelled"] is True

    await_args = mock_cancel_meeting.await_args
    assert await_args is not None
    meeting_id, current_user, db = await_args.args
    assert meeting_id == 1
    assert current_user.id == 2


def test_cancel_meeting_not_found(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.MANAGER)

    mock_cancel_meeting = AsyncMock(side_effect=meeting_services.MeetingNotFoundError())
    monkeypatch.setattr(meeting_services, "cancel_meeting", mock_cancel_meeting)

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.patch("/api/v1/meetings/999/cancel")
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert data["detail"] == "Meeting not found"

    await_args = mock_cancel_meeting.await_args
    assert await_args is not None
    meeting_id, current_user, db = await_args.args
    assert meeting_id == 999
    assert current_user.id == 2


def test_cancel_meeting_permission_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=2, team_id=1, role=UserRole.USER)

    mock_cancel_meeting = AsyncMock(
        side_effect=meeting_services.MeetingPermissionError()
    )
    monkeypatch.setattr(meeting_services, "cancel_meeting", mock_cancel_meeting)

    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.patch("/api/v1/meetings/1/cancel")
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert data["detail"] == "Not enough permissions"

    await_args = mock_cancel_meeting.await_args
    assert await_args is not None
    meeting_id, current_user, db = await_args.args
    assert meeting_id == 1
    assert current_user.id == 2
