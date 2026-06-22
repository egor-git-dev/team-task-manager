from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.models.users import User


@pytest.mark.asyncio
async def test_get_current_user(monkeypatch):
    user = User(id=1, email="test@example.com")

    async def fake_get_user_by_id(user_id, db):
        assert user_id == 1
        return user

    token = create_access_token("1")
    monkeypatch.setattr(deps, "get_user_by_id", fake_get_user_by_id)
    db = AsyncMock(spec=AsyncSession)

    result = await get_current_user(token, db)

    assert result is user


@pytest.mark.asyncio
async def test_current_user_invalid_subject():
    token = create_access_token("abc")
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token, db)
    assert exc.value.status_code == 401
    assert exc.value.headers is not None
    assert exc.value.headers["WWW-Authenticate"] == "Bearer"
    assert exc.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_current_user_not_found(monkeypatch):
    async def fake_get_user_by_id(user_id, db):
        return None

    monkeypatch.setattr(deps, "get_user_by_id", fake_get_user_by_id)
    db = AsyncMock(spec=AsyncSession)
    token = create_access_token("1")

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token, db)
    assert exc.value.status_code == 401
    assert exc.value.headers is not None
    assert exc.value.headers["WWW-Authenticate"] == "Bearer"
    assert exc.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_current_user_invalid_jwt():
    db = AsyncMock(spec=AsyncSession)

    with pytest.raises(HTTPException) as exc:
        await get_current_user("abc", db)
    assert exc.value.status_code == 401
    assert exc.value.headers is not None
    assert exc.value.headers["WWW-Authenticate"] == "Bearer"
    assert exc.value.detail == "Could not validate credentials"
