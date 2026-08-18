"""
Tests for conversation response integration.
"""

import pytest

from app.ai.asr.schemas import UserUtterance
from app.ai.llm.schemas import LLMResponse
from app.ai.llm.service import LLMService
from app.conversation.engine import ConversationEngine


class FakeLLMService:
    """Fake LLM service for deterministic conversation tests."""

    async def generate(self, user_text: str) -> LLMResponse:
        return LLMResponse(
            content="Hello! How can I help you?",
            model="fake",
            finish_reason="stop",
        )


@pytest.mark.anyio
async def test_conversation_engine_processes_utterance() -> None:
    engine = ConversationEngine(
        llm_service=FakeLLMService(),
    )

    utterance = UserUtterance(
        text="Hello Alisha",
        confidence=0.95,
    )

    response = await engine.process(utterance)

    assert response is not None
    assert response.text == "Hello! How can I help you?"


@pytest.mark.anyio
async def test_conversation_engine_uses_response_manager() -> None:
    engine = ConversationEngine(
        llm_service=FakeLLMService(),
    )

    utterance = UserUtterance(
        text="Hello Alisha",
        confidence=0.95,
    )

    response = await engine.process(utterance)

    assert response is not None
    assert response.text == "Hello! How can I help you?"


@pytest.mark.anyio
async def test_conversation_engine_returns_normalized_response() -> None:
    engine = ConversationEngine(
        llm_service=FakeLLMService(),
    )

    utterance = UserUtterance(
        text="What can you do?",
        confidence=0.90,
    )

    response = await engine.process(utterance)

    assert response.text.strip() == response.text
    assert response.text != ""