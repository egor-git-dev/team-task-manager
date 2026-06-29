from datetime import UTC, datetime
from unittest.mock import AsyncMock

from app.models.users import User, UserRole
from app.services import users as user_services


def test_register_user_success(client, monkeypatch):
    async def fake_register_user(user_data, db):
        return {
            "id": 1,
            "email": user_data.email,
            "is_active": True,
            "role": UserRole.USER,
            "created_at": datetime.now(UTC),
            "team_id": None,
        }

    monkeypatch.setattr(user_services, "register_user", fake_register_user)

    response = client.post(
        "/api/v1/users",
        json={"email": "test@example.com", "password": "12345678"},
    )
    data = response.json()

    assert response.status_code == 201
    assert data["email"] == "test@example.com"
    assert data["is_active"]
    assert data["role"] == "user"
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_user_with_existing_email(client, monkeypatch):
    async def fake_register_user(user_data, db):
        raise user_services.UserAlreadyExistsError()

    monkeypatch.setattr(user_services, "register_user", fake_register_user)
    response = client.post(
        "/api/v1/users",
        json={"email": "test@example.com", "password": "12345678"},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User already exists"


def test_get_user_by_id(client, monkeypatch):
    async def fake_get_user_by_id_or_raise(user_id, db):
        return {
            "id": user_id,
            "email": "test@example.com",
            "is_active": True,
            "role": UserRole.USER,
            "created_at": datetime.now(UTC),
            "team_id": None,
        }

    monkeypatch.setattr(
        user_services,
        "get_user_by_id_or_raise",
        fake_get_user_by_id_or_raise,
    )
    response = client.get("/api/v1/users/1")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert "hashed_password" not in data


def test_get_user_by_id_not_found(client, monkeypatch):
    async def fake_get_user_by_id_or_raise(user_id, db):
        raise user_services.UserNotFoundError()

    monkeypatch.setattr(
        user_services,
        "get_user_by_id_or_raise",
        fake_get_user_by_id_or_raise,
    )
    response = client.get("/api/v1/users/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_me(client, override_current_user):
    user = User(
        id=1,
        email="test@example.com",
        is_active=True,
        role=UserRole.USER,
        created_at=datetime.now(UTC),
    )
    override_current_user(user)

    response = client.get("/api/v1/users/me")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert "hashed_password" not in data


def test_update_me_success(client, override_current_user, monkeypatch):
    current_user = User(
        id=1,
        email="old@example.com",
        is_active=True,
        role=UserRole.USER,
        created_at=datetime.now(UTC),
    )
    updated_user = User(
        id=1,
        email="new@example.com",
        is_active=True,
        role=UserRole.USER,
        created_at=datetime.now(UTC),
    )
    override_current_user(current_user)
    mock_update_current_user = AsyncMock(return_value=updated_user)
    monkeypatch.setattr(user_services, "update_current_user", mock_update_current_user)

    response = client.patch("/api/v1/users/me", json={"email": "new@example.com"})
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["email"] == "new@example.com"
    assert data["is_active"] is True
    assert "password" not in data
    assert "hashed_password" not in data

    await_args = mock_update_current_user.await_args
    assert await_args is not None
    user_data, current_user_arg, db = await_args.args
    assert user_data.email == "new@example.com"
    assert current_user_arg.id == 1


def test_update_me_email_already_taken(client, override_current_user, monkeypatch):
    current_user = User(
        id=1,
        email="old@example.com",
        is_active=True,
        role=UserRole.USER,
        created_at=datetime.now(UTC),
    )
    override_current_user(current_user)
    mock_update_current_user = AsyncMock(
        side_effect=user_services.EmailAlreadyTakenError()
    )
    monkeypatch.setattr(user_services, "update_current_user", mock_update_current_user)

    response = client.patch("/api/v1/users/me", json={"email": "taken@example.com"})
    data = response.json()

    assert response.status_code == 409
    assert data["detail"] == "Email already taken"

    await_args = mock_update_current_user.await_args
    assert await_args is not None
    user_data, current_user_arg, db = await_args.args
    assert user_data.email == "taken@example.com"
    assert current_user_arg.id == 1


def test_deactivate_me_success(client, override_current_user, monkeypatch):
    current_user = User(
        id=1,
        email="test@example.com",
        is_active=True,
        role=UserRole.USER,
        created_at=datetime.now(UTC),
    )
    deactivated_user = User(
        id=1,
        email="test@example.com",
        is_active=False,
        role=UserRole.USER,
        created_at=datetime.now(UTC),
    )
    override_current_user(current_user)

    mock_deactivate_current_user = AsyncMock(return_value=deactivated_user)
    monkeypatch.setattr(
        user_services,
        "deactivate_current_user",
        mock_deactivate_current_user,
    )

    response = client.delete("/api/v1/users/me")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["email"] == "test@example.com"
    assert data["is_active"] is False

    await_args = mock_deactivate_current_user.await_args
    assert await_args is not None
    current_user_arg, db = await_args.args
    assert current_user_arg.id == 1
