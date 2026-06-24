import secrets
import string

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import teams as team_crud
from app.crud import users as user_crud
from app.models.teams import Team
from app.models.users import User
from app.schemas.teams import TeamCreate, TeamJoin


class TeamJoinCodeGenerationError(Exception):
    pass


class TeamNotFoundError(Exception):
    pass


class UserAlreadyInTeamError(Exception):
    pass


JOIN_CODE_ALPHABET = string.ascii_uppercase + string.digits
JOIN_CODE_LENGTH = 8
JOIN_CODE_GENERATION_ATTEMPTS = 10


def generate_join_code() -> str:
    return "".join(secrets.choice(JOIN_CODE_ALPHABET) for _ in range(JOIN_CODE_LENGTH))


async def create_team(team_data: TeamCreate, db: AsyncSession) -> Team:
    for _ in range(JOIN_CODE_GENERATION_ATTEMPTS):
        join_code = generate_join_code()
        if await team_crud.get_team_by_join_code(join_code, db) is None:
            return await team_crud.create_team(team_data, join_code, db)

    raise TeamJoinCodeGenerationError()


async def join_team_by_code(
    team_data: TeamJoin, current_user: User, db: AsyncSession
) -> User:
    team = await team_crud.get_team_by_join_code(team_data.join_code, db)
    if team is None:
        raise TeamNotFoundError()
    if current_user.team_id is not None:
        raise UserAlreadyInTeamError()
    return await user_crud.update_user_team(current_user, team.id, db)
