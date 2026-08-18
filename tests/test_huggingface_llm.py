"""
Tests for Hugging Face LLM provider.
"""

import pytest

from app.ai.llm.providers.huggingface import HuggingFaceLLM
from app.ai.llm.schemas import LLMMessage, LLMRequest


@pytest.mark.anyio
async def test_huggingface_llm_generates_response() -> None:
    llm = HuggingFaceLLM()

    request = LLMRequest(
        messages=[
            LLMMessage(
                role="user",
                content="Hello Alisha",
            )
        ]
    )

    response = await llm.generate(request)

    assert response is not None
    assert response.content != ""