"""SQLAlchemy database engine and session."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import BASE_DIR, DATABASE_URL


Base = declarative_base()


def _ensure_data_dir() -> None:
    data_dir = BASE_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)


_ensure_data_dir()

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency: yield a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables."""
    from api import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
