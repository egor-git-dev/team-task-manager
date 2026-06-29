from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.users import User
from app.schemas.users import UserCreate, UserRead, UserUpdate
from app.services import users as user_services

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        return await user_services.register_user(user_data, db)
    except user_services.UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)) -> User:
    try:
        return await user_services.get_user_by_id_or_raise(user_id, db)
    except user_services.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.delete("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def deactivate_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    return await user_services.deactivate_current_user(current_user, db)


@router.patch("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        return await user_services.update_current_user(user_data, current_user, db)
    except user_services.EmailAlreadyTakenError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already taken",
        )
