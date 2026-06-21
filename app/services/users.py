from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.users import create_user, get_user_by_email
from app.models.users import User
from app.schemas.users import UserCreate


class UserAlreadyExistsError(Exception):
    pass


async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise UserAlreadyExistsError()
    return await create_user(db, user_data)
