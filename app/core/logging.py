"""
Application logging configuration.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIRECTORY = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIRECTORY / "voice-assistant.log"


def setup_logging() -> None:
    """
    Configure console and rotating-file logging for the application.

    Runtime log files live in the project's top-level ``logs/`` directory,
    keeping generated data separate from application source code.
    """

    LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(
                LOG_FILE,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            ),
        ],
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger instance.

    Args:
        name: Usually __name__.

    Returns:
        Configured logger.
    """
    return logging.getLogger(name)
