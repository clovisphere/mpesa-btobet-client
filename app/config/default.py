import os
import secrets

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Dummy API")
    API_VERSION: str = "/api/v1"
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./demo.db")
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Broker
    XML_ALLOWED_CONTENT_TYPE: list[str] = ["application/xml", "text/xml"]
    DEFAULT_TIMEOUT: int = 10
    FAILED_REGISTRATION_STATUS_CODE: int = 3201
    BROKER_FAILURE_MESSAGE: str = "we are unable to process the request"
    BROKER_SUCCESS_MESSAGE: str = (
        """Payment result received (TransID: {TRANSACTION_ID})."""
    )

    class Config:
        case_sensitive = True


settings = Settings()
