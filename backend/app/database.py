"""Database utilities for the backend services.

This module centralises how SQLAlchemy engines and sessions are created so the
rest of the backend can focus on business logic.  The previous implementation
hard-coded a Postgres connection string which meant the backend crashed out of
the box (no running Postgres server in CI) and every test suite import tried to
install ``psycopg2``.  To keep the backend dependable we now:

* detect the database URL from environment variables with a safe SQLite default
* only apply QueuePool specific options when we are actually using Postgres
* lazily create a singleton engine that can be re-used across modules
* expose a FastAPI-friendly ``get_db`` dependency that always closes sessions

These changes keep the "build it backwards" goal on track by ensuring the
backend data layer is predictable before higher layers depend on it.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

DEFAULT_SQLITE_URL = "sqlite:///./flowstate.db"


def _should_use_queue_pool(database_url: str) -> bool:
    """Return ``True`` when the URL is for Postgres and benefits from pooling."""

    return database_url.startswith("postgresql")


def _pool_kwargs(database_url: str) -> dict:
    """Pool configuration that keeps sensible defaults for Postgres."""

    if not _should_use_queue_pool(database_url):
        return {}

    return {
        "poolclass": QueuePool,
        "pool_size": int(os.getenv("BACKEND_DB_POOL_SIZE", 20)),
        "max_overflow": int(os.getenv("BACKEND_DB_MAX_OVERFLOW", 10)),
        "pool_timeout": int(os.getenv("BACKEND_DB_POOL_TIMEOUT", 30)),
        "pool_recycle": int(os.getenv("BACKEND_DB_POOL_RECYCLE", 1800)),
    }


def _database_url() -> str:
    """Pick the best database URL from the environment."""

    return (
        os.getenv("BACKEND_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or DEFAULT_SQLITE_URL
    )


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return a cached SQLAlchemy engine.

    The engine is created lazily the first time this function is called which
    keeps import-time side effects to a minimum and helps pytest isolate tests.
    """

    url = _database_url()
    return create_engine(url, **_pool_kwargs(url))


def _create_session_factory() -> scoped_session:
    engine = get_engine()
    return scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )


# Use scoped_session to ensure thread safety in multi-threaded environments
SessionLocal = _create_session_factory()


def get_db() -> Generator:
    """FastAPI dependency that yields a session and guarantees cleanup."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        SessionLocal.remove()