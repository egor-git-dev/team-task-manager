from fastapi import FastAPI
from sqladmin import Admin

from app.admin.auth import AdminAuth
from app.admin.views import (
    CommentAdmin,
    EvaluationAdmin,
    MeetingAdmin,
    TaskAdmin,
    TeamAdmin,
    UserAdmin,
)
from app.api.v1.router import api_router as api_v1_router
from app.core.config import settings
from app.db.session import engine

app = FastAPI(
    title="Team Task Manager",
    version="0.1.0",
)

admin = Admin(
    app,
    engine,
    authentication_backend=AdminAuth(secret_key=settings.secret_key),
)
admin.add_view(UserAdmin)
admin.add_view(TeamAdmin)
admin.add_view(TaskAdmin)
admin.add_view(MeetingAdmin)
admin.add_view(EvaluationAdmin)
admin.add_view(CommentAdmin)

app.include_router(api_v1_router, prefix="/api/v1")
