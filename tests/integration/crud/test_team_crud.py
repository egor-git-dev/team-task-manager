import pytest

from app.crud import teams as team_crud
from app.models.teams import Team
from app.models.users import User
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


@pytest.mark.asyncio
async def test_get_team_with_members(async_session):
    team = Team(name="test team", join_code="TEST1234")
    users = [
        User(email="1@example.com", hashed_password="hashed", team=team),
        User(email="2@example.com", hashed_password="hashed", team=team),
    ]
    async_session.add(team)
    async_session.add_all(users)
    await async_session.commit()
    await async_session.refresh(team)

    result = await team_crud.get_team_with_members(team.id, async_session)

    assert result is not None
    emails = {user.email for user in result.users}
    assert emails == {"1@example.com", "2@example.com"}
    assert result.id == team.id
    assert len(result.users) == 2
