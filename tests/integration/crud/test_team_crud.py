import pytest

from app.crud import teams as team_crud
from app.schemas.teams import TeamCreate


@pytest.mark.asyncio
async def test_create_team(async_session):
    team_data = TeamCreate(name="test team")
    join_code = "TEST1234"
    team = await team_crud.create_team(team_data, join_code, async_session)

    assert team.name == "test team"
    assert team.join_code == "TEST1234"


@pytest.mark.asyncio
async def test_get_team_by_join_code(async_session):
    team_data = TeamCreate(name="test team")
    join_code = "TEST1234"
    await team_crud.create_team(team_data, join_code, async_session)
    result = await team_crud.get_team_by_join_code(
        join_code="TEST1234", db=async_session
    )

    assert result is not None
    assert result.name == "test team"
    assert result.join_code == "TEST1234"


@pytest.mark.asyncio
async def test_get_team_by_id(async_session):
    team_data = TeamCreate(name="test team")
    join_code = "TEST1234"
    team = await team_crud.create_team(team_data, join_code, async_session)
    result = await team_crud.get_team_by_id(team_id=team.id, db=async_session)

    assert result is not None
    assert result.name == "test team"
    assert result.join_code == "TEST1234"


@pytest.mark.asyncio
async def test_get_team_by_join_code_not_found(async_session):
    result = await team_crud.get_team_by_join_code(
        join_code="UNKNOWN", db=async_session
    )

    assert result is None
