from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.crud import users as user_crud
from app.crud.users import create_user, get_user_by_email, get_user_by_id
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class EmailAlreadyTakenError(Exception):
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


async def authenticate_user(email: str, password: str, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)
    if user is None:
        raise InvalidCredentialsError()
    if user.is_active is False:
        raise InvalidCredentialsError()
    if not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError()
    return user


async def deactivate_current_user(current_user: User, db: AsyncSession) -> User:
    return await user_crud.deactivate_user(current_user, db)


async def update_current_user(
    user_data: UserUpdate,
    current_user: User,
    db: AsyncSession,
) -> User:
    if user_data.email is not None:
        existing_user = await user_crud.get_user_by_email(user_data.email, db)
        if existing_user is not None and existing_user.id != current_user.id:
            raise EmailAlreadyTakenError()
    return await user_crud.update_user(current_user, user_data, db)
