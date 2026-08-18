import pytest
from unittest.mock import MagicMock, patch

from app.ai.llm.providers.huggingface import HuggingFaceLLM
from app.ai.llm.schemas import LLMMessage, LLMRequest


@pytest.mark.anyio
async def test_huggingface_llm_generates_response() -> None:

    llm = HuggingFaceLLM()

    # Mock the HuggingFace API response
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "I'm an AI assistant designed to help with voice conversations and answer questions."
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 20
    mock_response.usage.completion_tokens = 30
    mock_response.usage.total_tokens = 50

    # Create a mock client with synchronous chat.completions.create
    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = MagicMock(return_value=mock_response)

    # Patch the HuggingFaceLLM's _client with our mock
    with patch.object(llm, '_client', mock_client):
        request = LLMRequest(
            messages=[
                LLMMessage(
                    role="user",
                    content="Hello Alisha. Introduce yourself in one sentence.",
                )
            ],
            temperature=0.7,
            max_tokens=100,
        )

        response = await llm.generate(request)

        print()
        print("MODEL:", response.model)
        print("RESPONSE:", response.content)
        print("FINISH:", response.finish_reason)
        print("USAGE:", response.usage)

        assert response.content
        assert response.model
        assert response.content == "I'm an AI assistant designed to help with voice conversations and answer questions."
        assert response.finish_reason == "stop"
        assert response.usage["prompt_tokens"] == 20
        assert response.usage["completion_tokens"] == 30