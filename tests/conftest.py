"""Shared pytest configuration for the asyncio-native voice pipeline."""

from __future__ import annotations


import pytest


@pytest.fixture
def anyio_backend() -> str:
    """Run AnyIO tests with the backend used by Pipecat and ASR clients."""

    return "asyncio"