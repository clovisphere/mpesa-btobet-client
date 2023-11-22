from fastapi import Depends, FastAPI
from fastapi_health import health
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1 import api_router
from app.config.default import settings
from app.deps import get_db_session
from app.middleware.logging import LoggingMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_VERSION}/openapi.json"
)

app.add_middleware(LoggingMiddleware)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Used by: /health
# (shouldn't be used or call by anyone else)
def ping(db: Session = Depends(get_db_session)):
    return db


app.add_api_route("/health", health([ping]))  # how very basic ^health check 🌡️^ 😽

app.include_router(api_router, prefix=settings.API_VERSION)
