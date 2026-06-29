from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.crud.users import get_user_by_id
from app.db.session import AsyncSessionLocal
from app.services.users import InvalidCredentialsError, authenticate_user


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        if not isinstance(email, str) or not isinstance(password, str):
            return False

        async with AsyncSessionLocal() as db:
            try:
                user = await authenticate_user(email, password, db)
            except InvalidCredentialsError:
                return False

            if not user.is_active or not user.is_superuser:
                return False

            request.session.update({"admin_user_id": user.id})
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("admin_user_id")
        if user_id is None:
            return False

        async with AsyncSessionLocal() as db:
            user = await get_user_by_id(int(user_id), db)

        return bool(user and user.is_active and user.is_superuser)
