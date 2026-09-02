"""
Tests for the ASR utterance manager.
"""

from app.ai.asr.schemas import TranscriptionResult
from app.ai.asr.utterance_manager import UtteranceManager


def test_interim_results_do_not_emit_utterance() -> None:
    manager = UtteranceManager()

    result = manager.process(
        TranscriptionResult(
            transcript="Hello",
            is_final=False,
            speech_final=False,
            confidence=0.80,
        )
    )

    assert result is None


def test_final_segment_without_speech_end_does_not_emit_utterance() -> None:
    manager = UtteranceManager()

    result = manager.process(
        TranscriptionResult(
            transcript="Hello Alisha",
            is_final=True,
            speech_final=False,
            confidence=0.90,
        )
    )

    assert result is None


def test_speech_final_emits_user_utterance() -> None:
    manager = UtteranceManager()

    manager.process(
        TranscriptionResult(
            transcript="Hello Alisha",
            is_final=False,
            speech_final=False,
            confidence=0.90,
        )
    )

    utterance = manager.process(
        TranscriptionResult(
            transcript="Hello Alisha, how are you?",
            is_final=True,
            speech_final=True,
            confidence=0.95,
        )
    )

    assert utterance is not None
    assert utterance.text == "Hello Alisha, how are you?"
    assert utterance.confidence == 0.95


def test_new_utterance_starts_after_reset() -> None:
    manager = UtteranceManager()

    first = manager.process(
        TranscriptionResult(
            transcript="Hello Alisha",
            is_final=True,
            speech_final=True,
            confidence=0.95,
        )
    )

    assert first is not None
    assert first.text == "Hello Alisha"

    second = manager.process(
        TranscriptionResult(
            transcript="What can you do?",
            is_final=True,
            speech_final=True,
            confidence=0.92,
        )
    )

    assert second is not None
    assert second.text == "What can you do?"

def test_interim_results_replace_previous_hypothesis() -> None:
    manager = UtteranceManager()

    manager.process(
        TranscriptionResult(
            transcript="Hello",
            is_final=False,
            speech_final=False,
            confidence=0.80,
        )
    )

    manager.process(
        TranscriptionResult(
            transcript="Hello Alisha",
            is_final=False,
            speech_final=False,
            confidence=0.90,
        )
    )

    utterance = manager.process(
        TranscriptionResult(
            transcript="Hello Alisha, how are you?",
            is_final=True,
            speech_final=True,
            confidence=0.95,
        )
    )

    assert utterance is not None
    assert utterance.text == "Hello Alisha, how are you?"
    assert utterance.confidence == 0.95
