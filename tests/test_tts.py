"""
Tests for the TTS module.
"""

import pytest

from app.ai.tts.providers.deepgram import DeepgramTTS
from app.ai.tts.schemas import TTSRequest,TTSResponse
from app.ai.tts.service import TTSService


@pytest.mark.anyio
async def test_deepgram_tts_synthesizes_speech(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeStream:
        def getvalue(self) -> bytes:
            return b"fake-audio"

    class FakeResponse:
        stream = FakeStream()

    class FakeAudio:
        def generate(self, **kwargs):
            assert kwargs["text"] == "Hello Alisha"
            return FakeResponse()

    class FakeV1:
        audio = FakeAudio()

    class FakeSpeak:
        v1 = FakeV1()

    class FakeClient:
        speak = FakeSpeak()

    monkeypatch.setattr(
        "app.ai.tts.providers.deepgram.DeepgramClient",
        lambda api_key: FakeClient(),
    )

    monkeypatch.setattr(
        "app.ai.tts.providers.deepgram.settings.DEEPGRAM_TTS_API_KEY",
        "test-key",
    )

    provider = DeepgramTTS()

    request = TTSRequest(
        text="Hello Alisha",
    )

    response = await provider.synthesize(request)

    assert response.audio == b"fake-audio"
    assert response.content_type == "audio/mpeg"
    assert response.model == "aura-2-thalia-en"

@pytest.mark.anyio
async def test_tts_service_synthesizes_speech() -> None:
    class FakeProvider:
        async def synthesize(self, request):
            return TTSResponse(
                audio=b"fake-audio",
                content_type="audio/mpeg",
                model="fake-model",
            )

    service = TTSService(provider=FakeProvider())

    request = TTSRequest(
        text="Hello Alisha",
    )

    response = await service.synthesize(request)

    assert response.audio == b"fake-audio"
    assert response.content_type == "audio/mpeg"
    assert response.model == "fake-model"