import secrets
import string

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import teams as team_crud
from app.models.teams import Team
from app.schemas.teams import TeamCreate


class TeamJoinCodeGenerationError(Exception):
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
