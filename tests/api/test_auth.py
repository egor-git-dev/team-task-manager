from app.core import security
from app.models.users import User
from app.services import users as user_service


def test_login_user_success(client, monkeypatch):
    user = User(id=1, email="test@example.com")

    async def fake_authenticate_user(email, password, db):
        return user

    def fake_create_access_token(subject):
        assert subject == "1"
        return "fake_token"

    monkeypatch.setattr(user_service, "authenticate_user", fake_authenticate_user)
    monkeypatch.setattr(security, "create_access_token", fake_create_access_token)

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "12345678",
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["access_token"] == "fake_token"
    assert data["token_type"] == "bearer"


def test_login_user_with_invalid_credentials(client, monkeypatch):
    async def fake_authenticate_user(email, password, db):
        raise user_service.InvalidCredentialsError()

    monkeypatch.setattr(user_service, "authenticate_user", fake_authenticate_user)

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "12345678",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
    assert response.headers["WWW-Authenticate"] == "Bearer"
