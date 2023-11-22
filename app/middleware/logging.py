import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            client_host=request.client.host,  # type: ignore
            path=request.url.path,
            method=request.method,
            content_type=request.headers.get("content-type"),
            release="0.1.0",  # to be changed
            internal_request_id=str(uuid.uuid4()),
        )
        # call next handler
        response = await call_next(request)
        structlog.contextvars.bind_contextvars(
            status_code=response.status_code,
        )
        # exclude /health from producing logs
        if request.url.path != "/health":
            if 400 <= response.status_code < 500:
                logger.warn("client error 🫤")
            elif response.status_code >= 500:
                logger.error("server error 🫣")
            else:
                logger.info("🐾🐾 🤭 🐾🐾")
        return response
