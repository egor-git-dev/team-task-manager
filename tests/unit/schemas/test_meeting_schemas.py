from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.meetings import MeetingCreate


def test_create_meeting_valid():
    starts_at = datetime.now(UTC) + timedelta(days=1)
    ends_at = starts_at + timedelta(hours=1)

    meeting = MeetingCreate(
        title="Planning",
        description="Sprint planning",
        starts_at=starts_at,
        ends_at=ends_at,
        participant_id=1,
    )

    assert meeting.title == "Planning"
    assert meeting.description == "Sprint planning"
    assert meeting.starts_at == starts_at
    assert meeting.ends_at == ends_at
    assert meeting.participant_id == 1


def test_create_meeting_empty_title():
    starts_at = datetime.now(UTC) + timedelta(days=1)
    ends_at = starts_at + timedelta(hours=1)

    with pytest.raises(ValidationError):
        MeetingCreate(
            title="",
            description="Sprint planning",
            starts_at=starts_at,
            ends_at=ends_at,
            participant_id=1,
        )


def test_create_meeting_invalid_time_range():
    starts_at = datetime.now(UTC) + timedelta(days=1)
    ends_at = starts_at

    with pytest.raises(ValidationError):
        MeetingCreate(
            title="Planning",
            description="Sprint planning",
            starts_at=starts_at,
            ends_at=ends_at,
            participant_id=1,
        )


def test_create_meeting_invalid_participant_id():
    starts_at = datetime.now(UTC) + timedelta(days=1)
    ends_at = starts_at + timedelta(hours=1)

    with pytest.raises(ValidationError):
        MeetingCreate(
            title="Planning",
            description="Sprint planning",
            starts_at=starts_at,
            ends_at=ends_at,
            participant_id=0,
        )
