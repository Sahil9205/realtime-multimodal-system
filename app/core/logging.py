"""
Application logging configuration.
"""

import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure the root logger.
    """

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
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
