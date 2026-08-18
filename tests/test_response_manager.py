"""
Tests for the conversation response manager.
"""

from app.conversation.response.builder import ResponseBuilder
from app.conversation.response.manager import ResponseManager


def test_response_manager_returns_response() -> None:
    manager = ResponseManager()

    response = manager.create("Hello Alisha")

    assert response is not None
    assert response.text == "Hello Alisha"


def test_response_manager_uses_response_builder() -> None:
    builder = ResponseBuilder()
    manager = ResponseManager(builder=builder)

    response = manager.create("  Hello Alisha  ")

    assert response.text == "Hello Alisha"


def test_response_manager_handles_empty_response() -> None:
    manager = ResponseManager()

    response = manager.create("   ")

    assert response.text != ""