import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./demo.db")

# if using an sqlite database
if "sqlite:///./demo.db" == DATABASE_URL:
    connect_args = {"check_same_thread": False}
    pool_pre_ping = False
else:
    connect_args = {}
    pool_pre_ping = True

engine = create_engine(
    DATABASE_URL, connect_args=connect_args, pool_pre_ping=pool_pre_ping
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
