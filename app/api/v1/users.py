from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.users import User
from app.schemas.users import UserCreate, UserRead
from app.services import users as user_services


router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate, db: AsyncSession = Depends(get_db)
) -> User:
    try:
        return await user_services.register_user(user_data, db)
    except user_services.UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
