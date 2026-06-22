from fastapi import APIRouter

from app.api.v1 import auth, health, user_routes

api_router = APIRouter()


api_router.include_router(health.router)
api_router.include_router(user_routes.router)
api_router.include_router(auth.router)
