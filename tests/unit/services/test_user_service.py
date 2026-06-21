import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.users import UserCreate
from app.services import users as user_service
from app.services.users import UserAlreadyExistsError


@pytest.mark.asyncio
async def test_register_user_raises_if_email_exists(monkeypatch):
    async def fake_get_user_by_email(email, db):
        return object()

    monkeypatch.setattr(
        user_service,
        "get_user_by_email",
        fake_get_user_by_email,
    )
    db = AsyncMock(spec=AsyncSession)
    user_data = UserCreate(email="test@example.com", password="12345678")

    with pytest.raises(UserAlreadyExistsError):
        await user_service.register_user(user_data, db)


@pytest.mark.asyncio
async def test_register_user_if_email_not_exist(monkeypatch):
    created_user = object()

    async def fake_get_user_by_email(email, db):
        return None

    async def fake_create_user(user_data, db):
        return created_user

    monkeypatch.setattr(user_service, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(user_service, "create_user", fake_create_user)
    db = AsyncMock(spec=AsyncSession)
    user_data = UserCreate(email="test@example.com", password="12345678")
    result = await user_service.register_user(user_data, db)

    assert result is created_user
