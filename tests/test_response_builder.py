"""
Tests for the conversation response builder.
"""

from app.conversation.response.builder import ResponseBuilder


def test_response_builder_creates_response() -> None:
    builder = ResponseBuilder()

    response = builder.build("Hello Alisha")

    assert response is not None
    assert response.text == "Hello Alisha"


def test_response_builder_strips_whitespace() -> None:
    builder = ResponseBuilder()

    response = builder.build("  Hello Alisha  ")

    assert response.text == "Hello Alisha"


def test_response_builder_handles_empty_response() -> None:
    builder = ResponseBuilder()

    response = builder.build("   ")

    assert response.text != ""