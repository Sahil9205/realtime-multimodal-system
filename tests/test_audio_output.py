"""
Tests for the audio output module.
"""

import pytest

from app.ai.tts.schemas import TTSResponse
from app.audio.output.system import SystemAudioOutput


@pytest.mark.anyio
async def test_system_audio_output_accepts_audio(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = SystemAudioOutput()

    response = TTSResponse(
        audio=b"fake-audio-data",
        content_type="audio/mpeg",
        model="deepgram",
    )

    class FakeAudio:
        frame_rate = 16000

        def get_array_of_samples(self):
            return [0, 1, 2, 3]

    monkeypatch.setattr(
        "app.audio.output.system.AudioSegment.from_file",
        lambda *args, **kwargs: FakeAudio(),
    )

    monkeypatch.setattr(
        "app.audio.output.system.sd.play",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        "app.audio.output.system.sd.stop",
        lambda: None,
    )

    result = await output.play(response)

    assert result is None