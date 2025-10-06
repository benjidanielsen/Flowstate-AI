import logging
import sys
from pathlib import Path


def setup_logging(logger_name, log_file_name):
    """
    Sets up a standardized logger for the application.
    """
    project_root = Path(__file__).parent.parent
    log_dir = project_root / "godmode-logs"
    log_dir.mkdir(exist_ok=True)
    log_file_path = log_dir / log_file_name

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if already configured
    if logger.hasHandlers():
        return logger

    # Create a file handler with UTF-8 encoding
    file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter(
            f"🤖 [{logger_name}] %(asctime)s - %(levelname)s - %(message)s"
        )
    )

    # Create a stream handler (for console output) with UTF-8 encoding
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(
        logging.Formatter(
            f"🤖 [{logger_name}] %(asctime)s - %(levelname)s - %(message)s"
        )
    )

    # On Windows, reconfigure stdout to ensure it handles UTF-8
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except TypeError:
            # This might fail in some environments, but it's a good practice to try
            pass

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
