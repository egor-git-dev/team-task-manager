from datetime import datetime, UTC

from fastapi.testclient import TestClient

from app.main import app
from app.models.users import UserRole
from app.services import users as user_services

client = TestClient(app)


def test_register_user_success(monkeypatch):
    async def fake_register_user(user_data, db):
        return {
            "id": 1,
            "email": user_data.email,
            "is_active": True,
            "role": UserRole.USER,
            "created_at": datetime.now(UTC),
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


def test_register_user_with_existing_email(monkeypatch):
    async def fake_register_user(user_data, db):
        raise user_services.UserAlreadyExistsError

    monkeypatch.setattr(user_services, "register_user", fake_register_user)
    response = client.post(
        "/api/v1/users",
        json={"email": "test@example.com", "password": "12345678"},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User already exists"
