from fastapi import APIRouter

from app.api.v1 import (
    auth,
    calendar_routes,
    comment_routes,
    evaluation_routes,
    health,
    meeting_routes,
    task_routes,
    team_routes,
    user_routes,
)

api_router = APIRouter()


api_router.include_router(health.router)
api_router.include_router(user_routes.router)
api_router.include_router(auth.router)
api_router.include_router(task_routes.router)
api_router.include_router(team_routes.router)
api_router.include_router(comment_routes.router)
api_router.include_router(evaluation_routes.router)
api_router.include_router(meeting_routes.router)
api_router.include_router(calendar_routes.router)
