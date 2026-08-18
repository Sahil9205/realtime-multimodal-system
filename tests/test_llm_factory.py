from app.ai.llm.factory import create_llm
from app.ai.llm.providers.huggingface import HuggingFaceLLM
from app.core.exceptions import LLMError


def test_factory_creates_huggingface_provider() -> None:
    llm = create_llm()

    assert isinstance(llm, HuggingFaceLLM)


def test_factory_rejects_unsupported_provider(monkeypatch) -> None:
    from app.core.config import settings

    monkeypatch.setattr(
        settings,
        "LLM_PROVIDER",
        "unsupported",
    )

    try:
        create_llm()
        assert False
    except LLMError:
        pass