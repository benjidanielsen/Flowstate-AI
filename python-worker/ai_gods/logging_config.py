"""Simple logging configuration helper used by the python worker."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Return a logger configured with a basic formatter.

    Parameters
    ----------
    name:
        Name for the logger instance.
    log_file:
        Optional path to a file where log messages should be written. When
        provided, the path is created if missing and a file handler is
        attached in addition to the default stream handler.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(_LOG_FORMAT)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
