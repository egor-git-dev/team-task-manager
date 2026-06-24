import pytest

from app.crud import users as user_crud
from app.models.teams import Team
from app.models.users import User


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
