from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.users import User, UserRole
from app.schemas.users import UserCreate, UserUpdate


async def create_user(user_data: UserCreate, db: AsyncSession) -> User:
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def get_user_by_email(user_email: str, db: AsyncSession) -> User | None:
    query = select(User).where(User.email == user_email)
    result = await db.execute(query)

    return result.scalar_one_or_none()


async def get_user_by_id(user_id: int, db: AsyncSession) -> User | None:
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)

    return result.scalar_one_or_none()


async def update_user_team(user: User, team_id: int | None, db: AsyncSession) -> User:
    user.team_id = team_id
    await db.commit()
    await db.refresh(user)

    return user


async def update_user_role(user: User, role: UserRole, db: AsyncSession) -> User:
    user.role = role
    await db.commit()
    await db.refresh(user)

    return user


async def deactivate_user(user: User, db: AsyncSession) -> User:
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(user: User, user_data: UserUpdate, db: AsyncSession) -> User:
    update_data = user_data.model_dump(exclude_unset=True)

    if "email" in update_data:
        user.email = update_data["email"]

    if "password" in update_data:
        user.hashed_password = get_password_hash(update_data["password"])

    await db.commit()
    await db.refresh(user)
    return user
