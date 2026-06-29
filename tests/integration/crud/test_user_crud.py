import pytest

from app.core.security import verify_password
from app.crud import users as user_crud
from app.models.teams import Team
from app.models.users import User, UserRole
from app.schemas.users import UserUpdate


@pytest.mark.asyncio
async def test_update_user_team(async_session):
    user = User(email="test@example.com", hashed_password="hashed_password")
    team = Team(name="test team", join_code="TEST1234")
    async_session.add_all([user, team])
    await async_session.commit()
    await async_session.refresh(user)
    await async_session.refresh(team)
    updated_user = await user_crud.update_user_team(user, team.id, async_session)

    assert updated_user is user
    assert user.team_id == team.id

    no_team_user = await user_crud.update_user_team(user, None, async_session)

    assert no_team_user.team_id is None


@pytest.mark.asyncio
async def test_update_user_role(async_session):
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        role=UserRole.USER,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    updated_user = await user_crud.update_user_role(
        user,
        UserRole.MANAGER,
        async_session,
    )

    assert updated_user is user
    assert updated_user.role == UserRole.MANAGER


@pytest.mark.asyncio
async def test_update_user_email(async_session):
    user = User(email="old@example.com", hashed_password="hashed_password")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    user_data = UserUpdate(email="new@example.com")

    updated_user = await user_crud.update_user(user, user_data, async_session)

    assert updated_user.email == "new@example.com"
    assert updated_user.hashed_password == "hashed_password"


@pytest.mark.asyncio
async def test_update_user_password(async_session):
    user = User(email="test@example.com", hashed_password="old_hashed_password")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    user_data = UserUpdate(password="new_password_123")

    updated_user = await user_crud.update_user(user, user_data, async_session)

    assert updated_user.email == "test@example.com"
    assert updated_user.hashed_password != "old_hashed_password"
    assert verify_password("new_password_123", updated_user.hashed_password)


@pytest.mark.asyncio
async def test_deactivate_user(async_session):
    user = User(email="test@example.com", hashed_password="hashed_password")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    deactivated_user = await user_crud.deactivate_user(user, async_session)

    assert deactivated_user.is_active is False
