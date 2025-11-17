"""Regression tests for the backend database bootstrap."""

from pathlib import Path
import importlib
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

pytest.importorskip("sqlalchemy")


def _reload_database(monkeypatch, **env):
    """Reload the database module with the provided environment."""

    for key in ("BACKEND_DATABASE_URL", "DATABASE_URL"):
        monkeypatch.delenv(key, raising=False)

    for key, value in env.items():
        monkeypatch.setenv(key, value)

    import backend.app.database as database

    return importlib.reload(database)


def test_default_sqlite_engine(monkeypatch):
    database = _reload_database(monkeypatch)

    engine = database.get_engine()

    assert engine.url.drivername == "sqlite"
    assert str(engine.url).endswith("flowstate.db")


def test_env_override_uses_custom_database_url(monkeypatch, tmp_path):
    db_path = tmp_path / "custom.db"
    database = _reload_database(
        monkeypatch, BACKEND_DATABASE_URL=f"sqlite:///{db_path}"
    )

    engine = database.get_engine()

    assert engine.url.database == str(db_path)


def test_postgres_urls_enable_queue_pool(monkeypatch):
    database = _reload_database(
        monkeypatch,
        BACKEND_DATABASE_URL="postgresql://user:pass@localhost:5432/flowstate",
    )

    engine = database.get_engine()

    # QueuePool has a descriptive class name and a ``size`` attribute we expect
    # to be configurable via the new environment variables.
    assert engine.pool.__class__.__name__ == "QueuePool"
    assert engine.pool.size() == int(
        database.os.getenv("BACKEND_DB_POOL_SIZE", 20)
    )
