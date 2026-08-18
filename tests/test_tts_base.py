import pytest

from app.ai.tts.base import BaseTTS


def test_base_tts_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        BaseTTS()