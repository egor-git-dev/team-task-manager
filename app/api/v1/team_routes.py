from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.teams import Team
from app.models.users import User, UserRole
from app.schemas.teams import (
    TeamCreate,
    TeamJoin,
    TeamWithJoinCodeRead,
    TeamWithMembersRead,
)
from app.schemas.users import UserRead
from app.services import teams as team_services

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post(
    "", response_model=TeamWithJoinCodeRead, status_code=status.HTTP_201_CREATED
)
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


@router.post("/join", response_model=UserRead, status_code=status.HTTP_200_OK)
async def join_team_by_code(
    team_data: TeamJoin,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        return await team_services.join_team_by_code(team_data, current_user, db)
    except team_services.TeamNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    except team_services.UserAlreadyInTeamError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already in team",
        )


@router.get("/me", response_model=TeamWithMembersRead)
async def get_my_team(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Team:
    try:
        return await team_services.get_current_user_team_or_raise(current_user, db)
    except team_services.UserNotInTeamError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is not in a team",
        )
    except team_services.TeamNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
