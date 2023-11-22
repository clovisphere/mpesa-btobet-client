from fastapi import APIRouter

from app.api.api_v1.endpoints import payments

api_router = APIRouter()

# add known routes below
api_router.include_router(payments.router, prefix="/legacy/broker", tags=["broker"])
