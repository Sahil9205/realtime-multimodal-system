"""
Utilities for measuring execution time.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from collections.abc import Generator

from app.core.logging import get_logger


logger = get_logger(__name__)


@contextmanager
def timer(name: str) -> Generator[None, None, None]:
    """
    Measure the execution time of a block of code.

    Args:
        name: Name of the operation being measured.
    """
    start = time.perf_counter()

    try:
        yield
    finally:
        elapsed = (time.perf_counter() - start) * 1000
        logger.info("%s completed in %.2f ms", name, elapsed)