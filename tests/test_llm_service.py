import pytest

from app.ai.llm.base import BaseLLM
from app.ai.llm.schemas import LLMRequest, LLMResponse
from app.ai.llm.service import LLMService


class FakeLLM(BaseLLM):
    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        return LLMResponse(
            content=f"Fake response to: {request.messages[-1].content}",
            model="fake",
            finish_reason="stop",
        )


@pytest.mark.anyio
async def test_llm_service_generates_response() -> None:
    service = LLMService(llm=FakeLLM())

    response = await service.generate("Hello Alisha")

    assert response.content == "Fake response to: Hello Alisha"


@pytest.mark.anyio
async def test_llm_service_uses_provider() -> None:
    service = LLMService(llm=FakeLLM())

    response = await service.generate("What can you do?")

    assert response.model == "fake"
    assert "What can you do?" in response.content