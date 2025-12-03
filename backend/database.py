"""Database configuration that can switch between local SQLite and Azure SQL."""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQL_CONN_STR_ENV = "SQL_CONN_STR"
DEFAULT_SQLITE_URL = "sqlite:///./store.db"


def _build_engine_url() -> str:
    # Prefer the Azure SQL connection string if it is set
    conn_str = os.getenv(SQL_CONN_STR_ENV)
    if conn_str:
        return conn_str
    # Fallback to a local SQLite database for quick development
    return DEFAULT_SQLITE_URL


engine = create_engine(
    _build_engine_url(),
    connect_args={"check_same_thread": False} if "sqlite" in _build_engine_url() else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_all_tables() -> None:
    from . import models  # noqa: F401 (import populates metadata)

    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
