"""
Integration test for the ASR transcription pipeline.

Tests the flow from transcription results into
complete user utterances.
"""

from app.ai.asr.schemas import TranscriptionResult
from app.ai.asr.utterance_manager import UtteranceManager


def test_streaming_transcription_produces_user_utterance() -> None:
    """
    Simulate a streaming ASR session and verify that
    a speech-final result produces a complete utterance.
    """

    manager = UtteranceManager()

    # ----------------------------------------------------------
    # Interim ASR results
    # ----------------------------------------------------------

    result = manager.process(
        TranscriptionResult(
            transcript="Hello",
            is_final=False,
            speech_final=False,
            confidence=0.80,
        )
    )

    assert result is None

    result = manager.process(
        TranscriptionResult(
            transcript="Hello Alisha",
            is_final=False,
            speech_final=False,
            confidence=0.90,
        )
    )

    assert result is None

    # ----------------------------------------------------------
    # Final ASR result
    # ----------------------------------------------------------

    utterance = manager.process(
        TranscriptionResult(
            transcript="Hello Alisha",
            is_final=True,
            speech_final=True,
            confidence=0.95,
        )
    )

    assert utterance is not None
    assert utterance.text == "Hello Alisha"
    assert utterance.confidence == 0.95


def test_multiple_speech_segments_produce_multiple_utterances() -> None:
    """
    Verify that separate speech segments become separate
    user utterances.
    """

    manager = UtteranceManager()

    first = manager.process(
        TranscriptionResult(
            transcript="Hello Alisha",
            is_final=True,
            speech_final=True,
            confidence=0.95,
        )
    )

    second = manager.process(
        TranscriptionResult(
            transcript="What can you do?",
            is_final=True,
            speech_final=True,
            confidence=0.92,
        )
    )

    assert first is not None
    assert second is not None

    assert first.text == "Hello Alisha"
    assert second.text == "What can you do?"

    assert first.confidence == 0.95
    assert second.confidence == 0.92