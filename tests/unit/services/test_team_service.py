from unittest.mock import AsyncMock, call

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.teams import Team
from app.schemas.teams import TeamCreate
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
