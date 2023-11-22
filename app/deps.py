from typing import Generator

from sqlalchemy.orm import Session

from app.config.database import SessionLocal


def get_db_session() -> Generator:
    """returns a db session/connection."""
    session: Session | None = None
    try:
        session = SessionLocal()
        yield session
    finally:
        if session is not None:
            session.close()
