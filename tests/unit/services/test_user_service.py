from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate
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


@pytest.mark.asyncio
async def test_update_current_user_success_email(monkeypatch):
    mock_get_user_by_email = AsyncMock(return_value=None)
    monkeypatch.setattr(
        user_service.user_crud,
        "get_user_by_email",
        mock_get_user_by_email,
    )
    current_user = User(id=1, email="old@example.com")
    mock_update_user = AsyncMock(return_value=current_user)
    monkeypatch.setattr(
        user_service.user_crud,
        "update_user",
        mock_update_user,
    )

    user_data = UserUpdate(email="newemail@example.com")
    db = AsyncMock(spec=AsyncSession)

    result = await user_service.update_current_user(user_data, current_user, db)

    assert result is current_user
    mock_get_user_by_email.assert_awaited_once_with(user_data.email, db)
    mock_update_user.assert_awaited_once_with(current_user, user_data, db)


@pytest.mark.asyncio
async def test_update_current_user_email_already_taken(monkeypatch):
    current_user = User(id=1, email="old@example.com")
    existing_user = User(id=2, email="new@example.com")
    user_data = UserUpdate(email="new@example.com")
    db = AsyncMock(spec=AsyncSession)

    mock_get_user_by_email = AsyncMock(return_value=existing_user)
    mock_update_user = AsyncMock()

    monkeypatch.setattr(
        user_service.user_crud,
        "get_user_by_email",
        mock_get_user_by_email,
    )
    monkeypatch.setattr(
        user_service.user_crud,
        "update_user",
        mock_update_user,
    )

    with pytest.raises(user_service.EmailAlreadyTakenError):
        await user_service.update_current_user(user_data, current_user, db)

    mock_get_user_by_email.assert_awaited_once_with(user_data.email, db)
    mock_update_user.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_current_user_same_email_allowed(monkeypatch):
    current_user = User(id=1, email="same@example.com")
    existing_user = User(id=1, email="same@example.com")
    user_data = UserUpdate(email="same@example.com")
    db = AsyncMock(spec=AsyncSession)

    mock_get_user_by_email = AsyncMock(return_value=existing_user)
    mock_update_user = AsyncMock(return_value=current_user)

    monkeypatch.setattr(
        user_service.user_crud,
        "get_user_by_email",
        mock_get_user_by_email,
    )
    monkeypatch.setattr(
        user_service.user_crud,
        "update_user",
        mock_update_user,
    )

    result = await user_service.update_current_user(user_data, current_user, db)

    assert result is current_user
    mock_get_user_by_email.assert_awaited_once_with(user_data.email, db)
    mock_update_user.assert_awaited_once_with(current_user, user_data, db)


@pytest.mark.asyncio
async def test_deactivate_current_user_success(monkeypatch):
    current_user = User(id=1, email="test@example.com", is_active=True)
    deactivated_user = User(id=1, email="test@example.com", is_active=False)
    db = AsyncMock(spec=AsyncSession)

    mock_deactivate_user = AsyncMock(return_value=deactivated_user)
    monkeypatch.setattr(
        user_service.user_crud,
        "deactivate_user",
        mock_deactivate_user,
    )

    result = await user_service.deactivate_current_user(current_user, db)

    assert result is deactivated_user
    mock_deactivate_user.assert_awaited_once_with(current_user, db)


@pytest.mark.asyncio
async def test_authenticate_user_inactive_user_raises(monkeypatch):
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=False,
    )

    mock_get_user_by_email = AsyncMock(return_value=user)
    mock_verify_password = Mock(return_value=True)

    monkeypatch.setattr(user_service, "get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr(user_service, "verify_password", mock_verify_password)

    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(InvalidCredentialsError):
        await user_service.authenticate_user("test@example.com", "password", db)

    mock_get_user_by_email.assert_awaited_once_with("test@example.com", db)
    mock_verify_password.assert_not_called()
