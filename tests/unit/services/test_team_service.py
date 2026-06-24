from unittest.mock import AsyncMock, call

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.teams import Team
from app.models.users import User
from app.schemas.teams import TeamCreate, TeamJoin
from app.services import teams as team_services


def test_generate_join_code():
    join_code = team_services.generate_join_code()

    assert len(join_code) == 8


@pytest.mark.asyncio
async def test_create_team_with_first_generated_code(monkeypatch):
    team = Team(name="test team")
    mock_get_team_by_join_code = AsyncMock(return_value=None)
    mock_create_team = AsyncMock(return_value=team)
    monkeypatch.setattr(
        team_services.team_crud, "get_team_by_join_code", mock_get_team_by_join_code
    )
    monkeypatch.setattr(team_services.team_crud, "create_team", mock_create_team)

    team_data = TeamCreate(name="test team")
    db = AsyncMock(spec=AsyncSession)
    result = await team_services.create_team(team_data, db)

    assert result.name == "test team"
    await_args = mock_get_team_by_join_code.await_args
    assert await_args is not None
    join_code, db = await_args.args
    mock_get_team_by_join_code.assert_awaited_once_with(join_code, db)
    mock_create_team.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_team_if_first_generated_code_busy(monkeypatch):
    team = Team(name="test team")
    codes = iter(["BUSY1234", "FREE1234"])
    mock_get_team_by_join_code = AsyncMock(
        side_effect=[
            object(),
            None,
        ]
    )
    mock_create_team = AsyncMock(return_value=team)

    def fake_generate_join_code():
        return next(codes)

    monkeypatch.setattr(
        team_services.team_crud, "get_team_by_join_code", mock_get_team_by_join_code
    )
    monkeypatch.setattr(team_services, "generate_join_code", fake_generate_join_code)
    monkeypatch.setattr(team_services.team_crud, "create_team", mock_create_team)

    team_data = TeamCreate(name="test team")
    db = AsyncMock(spec=AsyncSession)
    result = await team_services.create_team(team_data, db)

    assert result.name == "test team"
    assert mock_get_team_by_join_code.await_count == 2
    mock_create_team.assert_awaited_once_with(team_data, "FREE1234", db)
    mock_get_team_by_join_code.assert_has_awaits(
        [
            call("BUSY1234", db),
            call("FREE1234", db),
        ]
    )


@pytest.mark.asyncio
async def test_create_team_generate_code_error(monkeypatch):
    mock_get_team_by_join_code = AsyncMock(return_value=object())
    monkeypatch.setattr(
        team_services.team_crud, "get_team_by_join_code", mock_get_team_by_join_code
    )
    team_data = TeamCreate(name="test team")
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(team_services.TeamJoinCodeGenerationError):
        await team_services.create_team(team_data, db)
    mock_get_team_by_join_code.assert_awaited()
    assert (
        mock_get_team_by_join_code.await_count
        == team_services.JOIN_CODE_GENERATION_ATTEMPTS
    )


@pytest.mark.asyncio
async def test_join_team_by_code_success(monkeypatch):
    team = Team(id=1, name="test team")
    mock_get_team_by_join_code = AsyncMock(return_value=team)
    monkeypatch.setattr(
        team_services.team_crud, "get_team_by_join_code", mock_get_team_by_join_code
    )
    updated_user = User(id=1, team_id=1)
    mock_update_user_team = AsyncMock(return_value=updated_user)
    monkeypatch.setattr(
        team_services.user_crud, "update_user_team", mock_update_user_team
    )
    team_data = TeamJoin(join_code="TEST1234")
    current_user = User()
    db = AsyncMock(spec=AsyncSession)
    result = await team_services.join_team_by_code(team_data, current_user, db)

    assert result is updated_user
    assert result.team_id == 1
    mock_update_user_team.assert_awaited_once_with(current_user, team.id, db)
    mock_get_team_by_join_code.assert_awaited_once_with("TEST1234", db)


@pytest.mark.asyncio
async def test_join_team_by_code_team_not_found(monkeypatch):
    mock_get_team_by_join_code = AsyncMock(return_value=None)
    monkeypatch.setattr(
        team_services.team_crud, "get_team_by_join_code", mock_get_team_by_join_code
    )
    mock_update_user_team = AsyncMock()
    monkeypatch.setattr(
        team_services.user_crud, "update_user_team", mock_update_user_team
    )
    team_data = TeamJoin(join_code="TEST1234")
    current_user = User()
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(team_services.TeamNotFoundError):
        await team_services.join_team_by_code(team_data, current_user, db)
    mock_get_team_by_join_code.assert_awaited_once_with("TEST1234", db)
    mock_update_user_team.assert_not_awaited()


@pytest.mark.asyncio
async def test_join_team_by_code_user_already_in_team(monkeypatch):
    team = Team(id=1, name="test team")
    mock_get_team_by_join_code = AsyncMock(return_value=team)
    monkeypatch.setattr(
        team_services.team_crud, "get_team_by_join_code", mock_get_team_by_join_code
    )
    mock_update_user_team = AsyncMock()
    monkeypatch.setattr(
        team_services.user_crud, "update_user_team", mock_update_user_team
    )
    team_data = TeamJoin(join_code="TEST1234")
    current_user = User(team_id=2)
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(team_services.UserAlreadyInTeamError):
        await team_services.join_team_by_code(team_data, current_user, db)
    mock_get_team_by_join_code.assert_awaited_once_with("TEST1234", db)
    mock_update_user_team.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_current_user_team_or_raise_success(monkeypatch):
    team = Team(id=1, name="test team")
    mock_get_team_with_members = AsyncMock(return_value=team)
    monkeypatch.setattr(
        team_services.team_crud, "get_team_with_members", mock_get_team_with_members
    )
    current_user = User(team_id=2)
    db = AsyncMock(spec=AsyncSession)
    result = await team_services.get_current_user_team_or_raise(current_user, db)

    assert result is team
    assert result.id == 1
    assert result.name == "test team"
    mock_get_team_with_members.assert_awaited_once_with(current_user.team_id, db)


@pytest.mark.asyncio
async def test_get_current_user_team_or_raise_user_not_in_team(monkeypatch):
    mock_get_team_with_members = AsyncMock()
    monkeypatch.setattr(
        team_services.team_crud, "get_team_with_members", mock_get_team_with_members
    )
    current_user = User(email="test@example.com", team_id=None)
    db = AsyncMock(spec=AsyncSession)
    with pytest.raises(team_services.UserNotInTeamError):
        await team_services.get_current_user_team_or_raise(current_user, db)
    mock_get_team_with_members.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_current_user_team_or_raise_team_not_found(monkeypatch):
    mock_get_team_with_members = AsyncMock(return_value=None)
    monkeypatch.setattr(
        team_services.team_crud, "get_team_with_members", mock_get_team_with_members
    )
    current_user = User(email="test@example.com", team_id=2)
    db = AsyncMock(spec=AsyncSession)
    with pytest.raises(team_services.TeamNotFoundError):
        await team_services.get_current_user_team_or_raise(current_user, db)
    mock_get_team_with_members.assert_awaited_once_with(current_user.team_id, db)
