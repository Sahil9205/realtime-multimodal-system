"""
Tests for voice response orchestration.
"""

import pytest

from app.ai.tts.schemas import TTSRequest, TTSResponse
from app.conversation.schemas.conversation_output import ConversationOutput
from app.voice.service import VoiceResponseService


class FakeTTSService:
    """Fake TTS service for deterministic testing."""

    def __init__(self) -> None:
        self.request: TTSRequest | None = None

    async def synthesize(
        self,
        request: TTSRequest,
    ) -> TTSResponse:
        self.request = request

        return TTSResponse(
            audio=b"fake-audio",
            content_type="audio/mpeg",
            model="fake-tts",
        )


class FakeAudioOutput:
    """Fake audio output for deterministic testing."""

    def __init__(self) -> None:
        self.response: TTSResponse | None = None
        self.interrupted = False

    async def play(
        self,
        response: TTSResponse,
    ) -> None:
        self.response = response

    async def interrupt(self) -> None:
        self.interrupted = True


@pytest.mark.anyio
async def test_voice_response_converts_conversation_to_audio() -> None:
    tts_service = FakeTTSService()
    audio_output = FakeAudioOutput()

    service = VoiceResponseService(
        tts_service=tts_service,
        audio_output=audio_output,
    )

    conversation_response = ConversationOutput(
        text="Hello! How can I help you?",
    )

    await service.respond(conversation_response)

    assert tts_service.request is not None
    assert tts_service.request.text == "Hello! How can I help you?"

    assert audio_output.response is not None
    assert audio_output.response.audio == b"fake-audio"
    assert audio_output.response.model == "fake-tts"


@pytest.mark.anyio
async def test_voice_response_interrupts_audio_output() -> None:
    audio_output = FakeAudioOutput()
    service = VoiceResponseService(audio_output=audio_output)

    await service.interrupt()

    assert audio_output.interrupted is True