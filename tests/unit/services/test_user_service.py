from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.schemas.users import UserCreate
from app.services import users as user_service
from app.services.users import InvalidCredentialsError, UserAlreadyExistsError


@pytest.mark.asyncio
async def test_register_user_raises_if_email_exists(monkeypatch):
    existing_user = object()

    mock_get_user_by_email = AsyncMock(return_value=existing_user)
    mock_create_user = AsyncMock()

    monkeypatch.setattr(user_service, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(user_service, "create_user", mock_create_user)

    db = AsyncMock(spec=AsyncSession)
    user_data = UserCreate(email="test@example.com", password="12345678")

    with pytest.raises(UserAlreadyExistsError):
        await user_service.register_user(user_data, db)

    mock_get_user_by_email.assert_awaited_once_with(user_data.email, db)
    mock_create_user.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_user_if_email_not_exist(monkeypatch):
    created_user = object()

    mock_get_user_by_email = AsyncMock(return_value=None)
    mock_create_user = AsyncMock(return_value=created_user)

    monkeypatch.setattr(user_service, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(user_service, "create_user", mock_create_user)

    db = AsyncMock(spec=AsyncSession)
    user_data = UserCreate(email="test@example.com", password="12345678")

    result = await user_service.register_user(user_data, db)

    assert result is created_user
    mock_get_user_by_email.assert_awaited_once_with(user_data.email, db)
    mock_create_user.assert_awaited_once_with(user_data, db)


@pytest.mark.asyncio
async def test_authenticate_user_success(monkeypatch):
    user = User(email="test@example.com", hashed_password="hashed_password")

    mock_get_user_by_email = AsyncMock(return_value=user)
    mock_verify_password = Mock(return_value=True)

    monkeypatch.setattr(user_service, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(user_service, "verify_password", mock_verify_password)

    db = AsyncMock(spec=AsyncSession)

    result = await user_service.authenticate_user(
        "test@example.com",
        "password",
        db,
    )

    assert result is user
    mock_get_user_by_email.assert_awaited_once_with("test@example.com", db)
    mock_verify_password.assert_called_once_with("password", "hashed_password")


@pytest.mark.asyncio
async def test_authenticate_user_not_found_email(monkeypatch):
    mock_get_user_by_email = AsyncMock(return_value=None)
    mock_verify_password = Mock()

    monkeypatch.setattr(user_service, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(user_service, "verify_password", mock_verify_password)

    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(InvalidCredentialsError):
        await user_service.authenticate_user("test@example.com", "password", db)

    mock_get_user_by_email.assert_awaited_once_with("test@example.com", db)
    mock_verify_password.assert_not_called()


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(monkeypatch):
    user = User(email="test@example.com", hashed_password="hashed_password")

    mock_get_user_by_email = AsyncMock(return_value=user)
    mock_verify_password = Mock(return_value=False)

    monkeypatch.setattr(user_service, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(user_service, "verify_password", mock_verify_password)

    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(InvalidCredentialsError):
        await user_service.authenticate_user("test@example.com", "password", db)

    mock_get_user_by_email.assert_awaited_once_with("test@example.com", db)
    mock_verify_password.assert_called_once_with("password", "hashed_password")
