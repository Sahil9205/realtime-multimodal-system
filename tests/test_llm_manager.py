import pytest

from app.ai.llm.base import BaseLLM
from app.ai.llm.manager import LLMManager
from app.ai.llm.schemas import LLMMessage, LLMRequest, LLMResponse


class FakeLLM(BaseLLM):
    async def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content=f"LLM response to: {request.messages[0].content}",
            model="fake",
            finish_reason="stop",
        )


@pytest.mark.anyio
async def test_llm_manager_generates_response() -> None:
    manager = LLMManager(
        llm=FakeLLM(),
    )

    request = LLMRequest(
        messages=[
            LLMMessage(
                role="user",
                content="Hello Assistant",
            )
        ]
    )

    response = await manager.generate(request)

    assert response.content == "LLM response to: Hello Assistant"


@pytest.mark.anyio
async def test_llm_manager_uses_injected_provider() -> None:
    llm = FakeLLM()
    manager = LLMManager(llm=llm)

    assert manager._llm is llm