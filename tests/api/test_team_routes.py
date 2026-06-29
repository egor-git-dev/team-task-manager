from datetime import UTC, datetime
from unittest.mock import AsyncMock

from app.models.teams import Team
from app.models.users import User, UserRole
from app.services import teams as team_services


def test_create_team_by_manager(client, override_current_user, monkeypatch):
    override_current_user(User(id=1, role=UserRole.MANAGER))

    team = Team(
        id=1, name="test team", join_code="TEST1234", created_at=datetime.now(UTC)
    )
    mock_create_team = AsyncMock(return_value=team)
    monkeypatch.setattr(team_services, "create_team", mock_create_team)

    response = client.post("/api/v1/teams", json={"name": "test_team"})

    assert response.status_code == 201
    assert response.json()["name"] == "test team"
    await_args = mock_create_team.await_args
    assert await_args is not None
    team_data, db = await_args.args
    assert team_data.name == "test_team"
    assert response.json()["join_code"] == "TEST1234"
    mock_create_team.assert_awaited_once()


def test_create_team_by_user(client, override_current_user, monkeypatch):
    override_current_user(User(id=1, role=UserRole.USER))

    mock_create_team = AsyncMock()
    monkeypatch.setattr(team_services, "create_team", mock_create_team)

    response = client.post("/api/v1/teams", json={"name": "test_team"})
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == "Not enough permissions"
    mock_create_team.assert_not_awaited()


def test_create_team_join_code_generation_error(
    client, override_current_user, monkeypatch
):
    override_current_user(User(id=1, role=UserRole.ADMIN))

    mock_create_team = AsyncMock(
        side_effect=team_services.TeamJoinCodeGenerationError()
    )
    monkeypatch.setattr(team_services, "create_team", mock_create_team)

    response = client.post("/api/v1/teams", json={"name": "test_team"})

    assert response.status_code == 500
    assert response.json()["detail"] == "Could not generate team join code"
    await_args = mock_create_team.await_args
    assert await_args is not None
    team_data, db = await_args.args
    assert team_data.name == "test_team"
    mock_create_team.assert_awaited_once()


def test_join_team_by_code_success(client, override_current_user, monkeypatch):
    override_current_user(User(id=1))
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

    response = client.post("/api/v1/teams/join", json={"join_code": "TEST1234"})
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["email"] == "test@example.com"
    mock_join_team_by_code.assert_awaited_once()
    await_args = mock_join_team_by_code.await_args
    assert await_args is not None
    team_data, current_user, db = await_args.args
    assert team_data.join_code == "TEST1234"
    assert current_user.id == 1


def test_join_team_by_code_team_not_found_error(
    client, override_current_user, monkeypatch
):
    override_current_user(User(id=1))
    mock_join_team_by_code = AsyncMock(side_effect=team_services.TeamNotFoundError())
    monkeypatch.setattr(team_services, "join_team_by_code", mock_join_team_by_code)

    response = client.post("/api/v1/teams/join", json={"join_code": "TEST1234"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Team not found"
    await_args = mock_join_team_by_code.await_args
    assert await_args is not None
    team_data, current_user, db = await_args.args
    assert team_data.join_code == "TEST1234"
    assert current_user.id == 1


def test_join_team_by_code_user_already_in_team_error(
    client, override_current_user, monkeypatch
):
    override_current_user(User(id=1))
    mock_join_team_by_code = AsyncMock(
        side_effect=team_services.UserAlreadyInTeamError()
    )
    monkeypatch.setattr(team_services, "join_team_by_code", mock_join_team_by_code)

    response = client.post("/api/v1/teams/join", json={"join_code": "TEST1234"})

    assert response.status_code == 409
    assert response.json()["detail"] == "User already in team"
    await_args = mock_join_team_by_code.await_args
    assert await_args is not None
    team_data, current_user, db = await_args.args
    assert team_data.join_code == "TEST1234"
    assert current_user.id == 1


def test_get_my_team_success(client, override_current_user, monkeypatch):
    override_current_user(User(id=1))
    team = Team(
        id=2,
        name="test team",
        created_at=datetime.now(UTC),
        users=[
            User(
                id=1,
                email="1@example.com",
                is_active=True,
                role=UserRole.USER,
                team_id=2,
                created_at=datetime.now(UTC),
            ),
            User(
                id=2,
                email="2@example.com",
                is_active=True,
                role=UserRole.USER,
                team_id=2,
                created_at=datetime.now(UTC),
            ),
            User(
                id=3,
                email="3@example.com",
                is_active=True,
                role=UserRole.USER,
                team_id=2,
                created_at=datetime.now(UTC),
            ),
        ],
    )
    mock_get_current_user_team_or_raise = AsyncMock(return_value=team)
    monkeypatch.setattr(
        team_services,
        "get_current_user_team_or_raise",
        mock_get_current_user_team_or_raise,
    )

    response = client.get("/api/v1/teams/me")
    data = response.json()

    assert response.status_code == 200
    assert len(data["users"]) == 3
    await_args = mock_get_current_user_team_or_raise.await_args
    assert await_args is not None
    current_user, db = await_args.args
    assert current_user.id == 1
    mock_get_current_user_team_or_raise.assert_awaited_once_with(current_user, db)


def test_get_my_team_user_not_in_team(client, override_current_user, monkeypatch):
    override_current_user(User(id=1))
    mock_get_current_user_team_or_raise = AsyncMock(
        side_effect=team_services.UserNotInTeamError()
    )
    monkeypatch.setattr(
        team_services,
        "get_current_user_team_or_raise",
        mock_get_current_user_team_or_raise,
    )

    response = client.get("/api/v1/teams/me")
    data = response.json()

    assert response.status_code == 409
    assert data["detail"] == "User is not in a team"
    await_args = mock_get_current_user_team_or_raise.await_args
    assert await_args is not None
    current_user, db = await_args.args
    assert current_user.id == 1
    mock_get_current_user_team_or_raise.assert_awaited_once()


def test_get_my_team_not_found(client, override_current_user, monkeypatch):
    override_current_user(User(id=1))
    mock_get_current_user_team_or_raise = AsyncMock(
        side_effect=team_services.TeamNotFoundError()
    )
    monkeypatch.setattr(
        team_services,
        "get_current_user_team_or_raise",
        mock_get_current_user_team_or_raise,
    )

    response = client.get("/api/v1/teams/me")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Team not found"
    await_args = mock_get_current_user_team_or_raise.await_args
    assert await_args is not None
    current_user, db = await_args.args
    assert current_user.id == 1
    mock_get_current_user_team_or_raise.assert_awaited_once()


def test_remove_team_member_success(client, override_current_user, monkeypatch):
    override_current_user(User(id=1, role=UserRole.MANAGER, team_id=2))

    mock_remove_team_member_or_raise = AsyncMock()
    monkeypatch.setattr(
        team_services,
        "remove_team_member_or_raise",
        mock_remove_team_member_or_raise,
    )

    response = client.delete("/api/v1/teams/members/5")

    assert response.status_code == 204
    mock_remove_team_member_or_raise.assert_awaited_once()
    await_args = mock_remove_team_member_or_raise.await_args
    assert await_args is not None
    user_id, current_user, db = await_args.args
    assert user_id == 5
    assert current_user.id == 1
    assert current_user.role == UserRole.MANAGER
    assert current_user.team_id == 2


def test_remove_team_member_team_permission_error(
    client, override_current_user, monkeypatch
):
    override_current_user(User(id=1, role=UserRole.MANAGER, team_id=2))
    mock_remove_team_member_or_raise = AsyncMock(
        side_effect=team_services.TeamPermissionError()
    )
    monkeypatch.setattr(
        team_services,
        "remove_team_member_or_raise",
        mock_remove_team_member_or_raise,
    )

    response = client.delete("/api/v1/teams/members/5")

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"
    mock_remove_team_member_or_raise.assert_awaited_once()
    await_args = mock_remove_team_member_or_raise.await_args
    assert await_args is not None
    user_id, current_user, db = await_args.args
    assert user_id == 5
    assert current_user.id == 1
    assert current_user.role == UserRole.MANAGER
    assert current_user.team_id == 2


def test_remove_team_member_user_not_in_team_error(
    client, override_current_user, monkeypatch
):
    override_current_user(User(id=1, role=UserRole.MANAGER, team_id=None))
    mock_remove_team_member_or_raise = AsyncMock(
        side_effect=team_services.UserNotInTeamError()
    )
    monkeypatch.setattr(
        team_services,
        "remove_team_member_or_raise",
        mock_remove_team_member_or_raise,
    )

    response = client.delete("/api/v1/teams/members/5")

    assert response.status_code == 409
    assert response.json()["detail"] == "User is not in a team"
    mock_remove_team_member_or_raise.assert_awaited_once()
    await_args = mock_remove_team_member_or_raise.await_args
    assert await_args is not None
    user_id, current_user, db = await_args.args
    assert user_id == 5
    assert current_user.id == 1
    assert current_user.role == UserRole.MANAGER
    assert current_user.team_id is None


def test_remove_team_member_cannot_remove_yourself_error(
    client,
    override_current_user,
    monkeypatch,
):
    override_current_user(User(id=1, role=UserRole.MANAGER, team_id=2))
    mock_remove_team_member_or_raise = AsyncMock(
        side_effect=team_services.CannotRemoveYourselfError()
    )
    monkeypatch.setattr(
        team_services,
        "remove_team_member_or_raise",
        mock_remove_team_member_or_raise,
    )

    response = client.delete("/api/v1/teams/members/5")

    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot remove yourself"
    mock_remove_team_member_or_raise.assert_awaited_once()
    await_args = mock_remove_team_member_or_raise.await_args
    assert await_args is not None
    user_id, current_user, db = await_args.args
    assert user_id == 5
    assert current_user.id == 1
    assert current_user.role == UserRole.MANAGER
    assert current_user.team_id == 2


def test_remove_team_member_not_found_error(client, override_current_user, monkeypatch):
    override_current_user(User(id=1, role=UserRole.MANAGER, team_id=2))
    mock_remove_team_member_or_raise = AsyncMock(
        side_effect=team_services.TeamMemberNotFoundError()
    )
    monkeypatch.setattr(
        team_services,
        "remove_team_member_or_raise",
        mock_remove_team_member_or_raise,
    )

    response = client.delete("/api/v1/teams/members/5")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
    mock_remove_team_member_or_raise.assert_awaited_once()
    await_args = mock_remove_team_member_or_raise.await_args
    assert await_args is not None
    user_id, current_user, db = await_args.args
    assert user_id == 5
    assert current_user.id == 1
    assert current_user.role == UserRole.MANAGER
    assert current_user.team_id == 2


def test_update_team_member_role_success(client, override_current_user, monkeypatch):
    override_current_user(User(id=1, role=UserRole.ADMIN, team_id=2))

    member = User(
        id=5,
        email="test@example.com",
        is_active=True,
        role=UserRole.MANAGER,
        team_id=2,
        created_at=datetime.now(UTC),
    )
    mock_update_team_member_role_or_raise = AsyncMock(return_value=member)
    monkeypatch.setattr(
        team_services,
        "update_team_member_role_or_raise",
        mock_update_team_member_role_or_raise,
    )

    response = client.patch("/api/v1/teams/members/5/role", json={"role": "manager"})
    data = response.json()

    assert response.status_code == 200
    assert data["role"] == "manager"
    mock_update_team_member_role_or_raise.assert_awaited_once()
    await_args = mock_update_team_member_role_or_raise.await_args
    assert await_args is not None
    member_id, role_data, current_user, db = await_args.args
    assert member_id == 5
    assert role_data.role == UserRole.MANAGER
    assert current_user.id == 1
    assert current_user.team_id == 2
    assert current_user.role == UserRole.ADMIN


def test_update_team_member_role_by_manager_permission_error(
    client,
    override_current_user,
    monkeypatch,
):
    override_current_user(User(id=1, role=UserRole.MANAGER, team_id=2))

    mock_update_team_member_role_or_raise = AsyncMock(
        side_effect=team_services.TeamPermissionError()
    )
    monkeypatch.setattr(
        team_services,
        "update_team_member_role_or_raise",
        mock_update_team_member_role_or_raise,
    )

    response = client.patch("/api/v1/teams/members/5/role", json={"role": "manager"})
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == "Not enough permissions"
    mock_update_team_member_role_or_raise.assert_awaited_once()
    await_args = mock_update_team_member_role_or_raise.await_args
    assert await_args is not None
    member_id, role_data, current_user, db = await_args.args
    assert member_id == 5
    assert role_data.role == UserRole.MANAGER
    assert current_user.id == 1
    assert current_user.team_id == 2
    assert current_user.role == UserRole.MANAGER


def test_update_team_member_role_user_not_in_team_error(
    client,
    override_current_user,
    monkeypatch,
):
    override_current_user(User(id=1, role=UserRole.MANAGER, team_id=None))

    mock_update_team_member_role_or_raise = AsyncMock(
        side_effect=team_services.UserNotInTeamError()
    )
    monkeypatch.setattr(
        team_services,
        "update_team_member_role_or_raise",
        mock_update_team_member_role_or_raise,
    )

    response = client.patch("/api/v1/teams/members/5/role", json={"role": "manager"})
    data = response.json()

    assert response.status_code == 409
    assert data["detail"] == "User is not in a team"
    mock_update_team_member_role_or_raise.assert_awaited_once()
    await_args = mock_update_team_member_role_or_raise.await_args
    assert await_args is not None
    member_id, role_data, current_user, db = await_args.args
    assert member_id == 5
    assert role_data.role == UserRole.MANAGER
    assert current_user.id == 1
    assert current_user.team_id is None
    assert current_user.role == UserRole.MANAGER


def test_update_team_member_role_cannot_update_yourself_error(
    client,
    override_current_user,
    monkeypatch,
):
    override_current_user(User(id=1, role=UserRole.ADMIN, team_id=2))
    mock_update_team_member_role_or_raise = AsyncMock(
        side_effect=team_services.CannotUpdateYourRoleError()
    )
    monkeypatch.setattr(
        team_services,
        "update_team_member_role_or_raise",
        mock_update_team_member_role_or_raise,
    )

    response = client.patch("/api/v1/teams/members/1/role", json={"role": "manager"})
    data = response.json()

    assert response.status_code == 409
    assert data["detail"] == "Cannot update your own role"
    mock_update_team_member_role_or_raise.assert_awaited_once()
    await_args = mock_update_team_member_role_or_raise.await_args
    assert await_args is not None
    member_id, role_data, current_user, db = await_args.args
    assert member_id == 1
    assert role_data.role == UserRole.MANAGER
    assert current_user.id == 1
    assert current_user.team_id == 2
    assert current_user.role == UserRole.ADMIN


def test_update_team_member_role_team_member_not_found(
    client,
    override_current_user,
    monkeypatch,
):
    override_current_user(User(id=1, role=UserRole.ADMIN, team_id=2))

    mock_update_team_member_role_or_raise = AsyncMock(
        side_effect=team_services.TeamMemberNotFoundError()
    )
    monkeypatch.setattr(
        team_services,
        "update_team_member_role_or_raise",
        mock_update_team_member_role_or_raise,
    )

    response = client.patch("/api/v1/teams/members/5/role", json={"role": "manager"})
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "User not found"
    mock_update_team_member_role_or_raise.assert_awaited_once()
    await_args = mock_update_team_member_role_or_raise.await_args
    assert await_args is not None
    member_id, role_data, current_user, db = await_args.args
    assert member_id == 5
    assert role_data.role == UserRole.MANAGER
    assert current_user.id == 1
    assert current_user.team_id == 2
    assert current_user.role == UserRole.ADMIN
