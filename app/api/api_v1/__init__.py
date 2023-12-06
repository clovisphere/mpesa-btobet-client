from fastapi import APIRouter

from app.api.api_v1.endpoints import payments, profiles

api_router = APIRouter()

# add known routes below
api_router.include_router(profiles.router, prefix="/profile", tags=["profile"])
api_router.include_router(payments.router, prefix="/legacy/broker", tags=["broker"])
