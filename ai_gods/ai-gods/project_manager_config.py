"""Configuration helpers for the enhanced Project Manager AI."""
from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional


@dataclass(frozen=True)
class ProjectManagerConfig:
    """Runtime configuration for :mod:`project_manager_enhanced`."""

    redis_host: str
    redis_port: int
    redis_password: Optional[str]
    db_path: Path
    log_path: Path

    def to_dict(self) -> Dict[str, str]:
        """Return a serialisable representation of the configuration."""
        data = asdict(self)
        data["db_path"] = str(self.db_path)
        data["log_path"] = str(self.log_path)
        return data


def load_project_manager_config(project_root: Optional[Path] = None) -> ProjectManagerConfig:
    """Load configuration values from environment variables.

    Parameters
    ----------
    project_root:
        Base path used to resolve relative filesystem locations. When ``None``
        the repository root is derived from the location of this file.
    """

    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent

    redis_host = os.getenv("GODMODE_REDIS_HOST", "localhost")
    redis_port = _read_int_env("GODMODE_REDIS_PORT", default=6379)
    redis_password = os.getenv("GODMODE_REDIS_PASSWORD")
    db_path = _resolve_path(os.getenv("GODMODE_DB_PATH", "godmode-state.db"), project_root)
    log_path = _resolve_path(
        os.getenv("GODMODE_PM_LOG_PATH", "godmode-logs/project-manager-enhanced.log"),
        project_root,
    )

    log_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return ProjectManagerConfig(
        redis_host=redis_host,
        redis_port=redis_port,
        redis_password=redis_password,
        db_path=db_path,
        log_path=log_path,
    )


def _read_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        return int(raw_value)
    except ValueError:
        print(
            f"[project_manager_config] Invalid value for {name!r}: {raw_value!r}. "
            f"Using default {default}."
        )
        return default


def _resolve_path(path_value: str, project_root: Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return project_root / path
