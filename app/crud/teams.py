from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.teams import Team
from app.schemas.teams import TeamCreate


async def create_team(team_data: TeamCreate, join_code: str, db: AsyncSession) -> Team:
    team = Team(
        name=team_data.name,
        join_code=join_code,
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)

    return team


async def get_team_by_join_code(join_code: str, db: AsyncSession) -> Team | None:
    query = select(Team).where(Team.join_code == join_code)
    result = await db.execute(query)

    return result.scalar_one_or_none()


async def get_team_by_id(team_id: int, db: AsyncSession) -> Team | None:
    query = select(Team).where(Team.id == team_id)
    result = await db.execute(query)

    return result.scalar_one_or_none()


async def get_team_with_members(team_id: int, db: AsyncSession) -> Team | None:
    query = select(Team).where(Team.id == team_id).options(selectinload(Team.users))
    result = await db.execute(query)

    return result.scalar_one_or_none()
