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


def test_join_team_by_code_success(monkeypatch):
    async def fake_get_current_user():
        return User(id=1)

    updated_user = User(
        id=1,
        email="test@example.com",
        is_active=True,
        role=UserRole.USER,
        team_id=2,
        created_at=datetime.now(UTC),
    )
    mock_join_team_by_code = AsyncMock(return_value=updated_user)
    monkeypatch.setattr(team_services, "join_team_by_code", mock_join_team_by_code)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post("/api/v1/teams/join", json={"join_code": "TEST1234"})
        data = response.json()
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["email"] == "test@example.com"
    mock_join_team_by_code.assert_awaited_once()
    await_args = mock_join_team_by_code.await_args
    assert await_args is not None
    team_data, current_user, db = await_args.args
    assert team_data.join_code == "TEST1234"
    assert current_user.id == 1


def test_join_team_by_code_team_not_found_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=1)

    mock_join_team_by_code = AsyncMock(side_effect=team_services.TeamNotFoundError())
    monkeypatch.setattr(team_services, "join_team_by_code", mock_join_team_by_code)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post("/api/v1/teams/join", json={"join_code": "TEST1234"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "Team not found"
    await_args = mock_join_team_by_code.await_args
    assert await_args is not None
    team_data, current_user, db = await_args.args
    assert team_data.join_code == "TEST1234"
    assert current_user.id == 1


def test_join_team_by_code_user_already_in_team_error(monkeypatch):
    async def fake_get_current_user():
        return User(id=1)

    mock_join_team_by_code = AsyncMock(
        side_effect=team_services.UserAlreadyInTeamError()
    )
    monkeypatch.setattr(team_services, "join_team_by_code", mock_join_team_by_code)
    app.dependency_overrides[get_current_user] = fake_get_current_user
    try:
        response = client.post("/api/v1/teams/join", json={"join_code": "TEST1234"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json()["detail"] == "User already in team"
    await_args = mock_join_team_by_code.await_args
    assert await_args is not None
    team_data, current_user, db = await_args.args
    assert team_data.join_code == "TEST1234"
    assert current_user.id == 1
