import pytest

from app.crud import users as user_crud
from app.models.teams import Team
from app.models.users import User, UserRole


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
