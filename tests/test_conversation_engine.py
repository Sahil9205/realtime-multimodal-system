"""
Tests for the conversation engine.
"""

import pytest

from app.ai.llm.schemas import LLMResponse
from app.ai.asr.schemas import UserUtterance
from app.conversation.engine import ConversationEngine


class EchoLLMService:
    async def generate(self, user_text: str) -> LLMResponse:
        return LLMResponse(
            content=user_text,
            model="fake-model",
            finish_reason="stop",
        )


class RecordingLLMService:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    async def generate(self, user_text: str) -> LLMResponse:
        self.prompts.append(user_text)
        return LLMResponse(
            content=f"Response {len(self.prompts)}",
            model="test",
            finish_reason="stop",
        )

@pytest.mark.anyio
async def test_conversation_engine_processes_greeting() -> None:
    engine = ConversationEngine(llm_service=EchoLLMService())

    utterance = UserUtterance(
        text="Hello",
        confidence=0.95,
    )

    response = await engine.process(utterance)

    assert response is not None
    assert "Hello" in response.text

@pytest.mark.anyio
async def test_conversation_engine_processes_information_request() -> None:
    engine = ConversationEngine(llm_service=EchoLLMService())

    utterance = UserUtterance(
        text="What can you do?",
        confidence=0.90,
    )

    response = await engine.process(utterance)

    assert response is not None
    assert "What can you do?" in response.text

@pytest.mark.anyio
async def test_conversation_engine_accepts_missing_confidence() -> None:
    engine = ConversationEngine(llm_service=EchoLLMService())

    utterance = UserUtterance(
        text="Hello",
        confidence=None,
    )

    response = await engine.process(utterance)

    assert response is not None


@pytest.mark.anyio
async def test_conversation_engine_keeps_context_across_turns() -> None:
    llm_service = RecordingLLMService()
    engine = ConversationEngine(llm_service=llm_service)

    await engine.process(UserUtterance(text="My name is Sahil", confidence=0.9))
    await engine.process(UserUtterance(text="What is my name?", confidence=0.9))

    assert len(llm_service.prompts) == 2
    assert "My name is Sahil" in llm_service.prompts[1]
    assert "Response 1" in llm_service.prompts[1]
    assert "What is my name?" in llm_service.prompts[1]