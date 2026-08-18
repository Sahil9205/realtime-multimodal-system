import pytest

from app.ai.llm.manager import LLMManager
from app.ai.llm.providers.huggingface import HuggingFaceLLM
from app.ai.llm.schemas import LLMMessage, LLMRequest


@pytest.mark.anyio
async def test_llm_manager_generates_response() -> None:
    manager = LLMManager(
        llm=HuggingFaceLLM(),
    )

    request = LLMRequest(
        messages=[
            LLMMessage(
                role="user",
                content="Hello Alisha",
            )
        ]
    )

    response = await manager.generate(request)

    assert response.content == "LLM response to: Hello Alisha"


@pytest.mark.anyio
async def test_llm_manager_uses_injected_provider() -> None:
    llm = HuggingFaceLLM()
    manager = LLMManager(llm=llm)

    assert manager._llm is llm