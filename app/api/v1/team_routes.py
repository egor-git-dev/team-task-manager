from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.teams import Team
from app.models.users import User, UserRole
from app.schemas.teams import TeamCreate, TeamRead
from app.services import teams as team_services

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Team:
    if current_user.role not in {UserRole.MANAGER, UserRole.ADMIN}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    try:
        return await team_services.create_team(team_data, db)
    except team_services.TeamJoinCodeGenerationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate team join code",
        )
