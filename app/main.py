from fastapi import Depends, FastAPI, Response, status

from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1 import api_router
from app.config.default import settings
from app.deps import get_db_session
from app.middleware.logging import LoggingMiddleware
from app.schema.health import Health

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

# our very basic ^health check 🌡️^ 😽
@app.get(
    "/health",
    tags=["health-check"],
    summary="Perform a health check",
    status_code=status.HTTP_200_OK,
    response_model=Health
)
def health(response: Response, db: Session = Depends(get_db_session)) -> Health:
    message = "healthy 😊"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        message = "unhealthy 😕"
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return Health(status=message)


app.include_router(api_router, prefix=settings.API_VERSION)
