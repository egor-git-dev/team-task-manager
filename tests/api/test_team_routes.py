from datetime import UTC, datetime
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app
from app.models.teams import Team
from app.models.users import User, UserRole
from app.services import teams as team_services

client = TestClient(app)


def test_create_team_by_manager(monkeypatch):
    async def fake_get_current_user():
        return User(id=1, role=UserRole.MANAGER)

    team = Team(
        id=1, name="test team", join_code="TEST1234", created_at=datetime.now(UTC)
    )
    mock_create_team = AsyncMock(return_value=team)
    monkeypatch.setattr(team_services, "create_team", mock_create_team)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post("/api/v1/teams", json={"name": "test_team"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["name"] == "test team"
    await_args = mock_create_team.await_args
    assert await_args is not None
    team_data, db = await_args.args
    assert team_data.name == "test_team"
    mock_create_team.assert_awaited_once()


def test_create_team_by_user(monkeypatch):
    async def fake_get_current_user():
        return User(id=1, role=UserRole.USER)

    mock_create_team = AsyncMock()
    monkeypatch.setattr(team_services, "create_team", mock_create_team)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post("/api/v1/teams", json={"name": "test_team"})
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert data["detail"] == "Not enough permissions"
    mock_create_team.assert_not_awaited()


def test_create_team_join_code_generation_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=1, role=UserRole.ADMIN)

    mock_create_team = AsyncMock(
        side_effect=team_services.TeamJoinCodeGenerationError()
    )
    monkeypatch.setattr(team_services, "create_team", mock_create_team)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post("/api/v1/teams", json={"name": "test_team"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    assert response.json()["detail"] == "Could not generate team join code"
    await_args = mock_create_team.await_args
    assert await_args is not None
    team_data, db = await_args.args
    assert team_data.name == "test_team"
    mock_create_team.assert_awaited_once()
