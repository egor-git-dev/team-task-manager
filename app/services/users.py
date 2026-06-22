from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.users import create_user, get_user_by_email, get_user_by_id
from app.models.users import User
from app.schemas.users import UserCreate


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


async def register_user(user_data: UserCreate, db: AsyncSession) -> User:
    existing_user = await get_user_by_email(user_data.email, db)
    if existing_user:
        raise UserAlreadyExistsError()
    return await create_user(user_data, db)


async def get_user_by_id_or_raise(user_id: int, db: AsyncSession) -> User:
    user = await get_user_by_id(user_id, db)
    if user is None:
        raise UserNotFoundError()
    return user
