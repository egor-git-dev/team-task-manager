import pytest
from pydantic import ValidationError

from app.schemas.teams import TeamCreate, TeamJoin


def test_valid_name():
    team = TeamCreate(name="valid name")
    assert team.name == "valid name"


def test_empty_string_name():
    with pytest.raises(ValidationError):
        TeamCreate(name="")


def test_too_long_name():
    with pytest.raises(ValidationError):
        TeamCreate(
            name="Tooooooooooooooo looooooooooooooooooooooooooooong"
            "naaaaaaaaaaaaaaaaaaaaaaaaammmmmeeeeeeeeeeeeeeeeeeeeeee"
        )


def test_valid_team_join_code():
    team_join = TeamJoin(join_code="valid code")
    assert team_join.join_code == "valid code"


def test_too_short_join_code():
    with pytest.raises(ValidationError):
        TeamJoin(join_code="inval")
