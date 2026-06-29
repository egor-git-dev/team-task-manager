from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.users import get_user_by_id
from app.db.session import AsyncSessionLocal
from app.models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token=token,
            key=settings.secret_key,
            algorithms=[settings.algorithm],
        )
        sub = payload.get("sub")
        if sub is None:
            raise credential_exception
        user_id = int(sub)
    except (JWTError, ValueError):
        raise credential_exception
    user = await get_user_by_id(user_id, db)

    if user is None:
        raise credential_exception
    if user.is_active is False:
        raise credential_exception
    return user
