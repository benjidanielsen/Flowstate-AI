"""Basic logging configuration used by the worker tests."""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"


def setup_logging(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Return a configured logger compatible with the worker expectations.

    The production code imports :mod:`ai_gods.logging_config` which was missing in
    the repository.  This lightweight stand-in configures a basic logger and, if
    a ``log_file`` is provided, attaches a rotating file handler so the worker can
    continue to run in development environments.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(_LOG_FORMAT)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(log_path, maxBytes=1_048_576, backupCount=3)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger

