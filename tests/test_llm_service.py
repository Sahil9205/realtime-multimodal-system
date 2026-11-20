import pytest

from app.ai.llm.base import BaseLLM
from app.ai.llm.schemas import LLMRequest, LLMResponse
from app.ai.llm.service import LLMService


class FakeLLM(BaseLLM):
    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(
            content=f"Fake response to: {request.messages[-1].content}",
            model="fake",
            finish_reason="stop",
        )


@pytest.mark.anyio
async def test_llm_service_generates_response() -> None:
    service = LLMService(llm=FakeLLM())

    response = await service.generate("Hello Assistant")

    assert response.content == "Fake response to: Hello Assistant"


@pytest.mark.anyio
async def test_llm_service_uses_provider() -> None:
    service = LLMService(llm=FakeLLM())

    response = await service.generate("What can you do?")

    assert response.model == "fake"
    assert "What can you do?" in response.content


@pytest.mark.anyio
async def test_llm_service_sends_voice_assistant_system_prompt() -> None:
    llm = FakeLLM()
    service = LLMService(llm=llm)

    await service.generate("My name is Sahil")

    assert llm.requests[0].messages[0].role == "system"
    assert "remember facts" in llm.requests[0].messages[0].content
    assert llm.requests[0].messages[-1].role == "user"