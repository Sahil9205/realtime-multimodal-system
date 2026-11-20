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
            transcript="Hello Assistant",
            is_final=True,
            speech_final=False,
            confidence=0.90,
        )
    )

    assert result is None


def test_explicit_stop_flushes_final_segment() -> None:
    manager = UtteranceManager()

    result = manager.process(
        TranscriptionResult(
            transcript="This is my complete request",
            is_final=True,
            speech_final=False,
            confidence=0.96,
        ),
        force_finalize=True,
    )

    assert result is not None
    assert result.text == "This is my complete request"


def test_final_segments_are_combined_until_speech_ends() -> None:
    manager = UtteranceManager()

    manager.process(
        TranscriptionResult(
            transcript="Can you tell me about",
            is_final=True,
            speech_final=False,
            confidence=0.9,
        )
    )

    utterance = manager.process(
        TranscriptionResult(
            transcript="famous Indian restaurants",
            is_final=True,
            speech_final=True,
            confidence=0.95,
        )
    )

    assert utterance is not None
    assert utterance.text == "Can you tell me about famous Indian restaurants"


def test_speech_final_emits_user_utterance() -> None:
    manager = UtteranceManager()

    manager.process(
        TranscriptionResult(
            transcript="Hello Assistant",
            is_final=False,
            speech_final=False,
            confidence=0.90,
        )
    )

    utterance = manager.process(
        TranscriptionResult(
            transcript="Hello Assistant, how are you?",
            is_final=True,
            speech_final=True,
            confidence=0.95,
        )
    )

    assert utterance is not None
    assert utterance.text == "Hello Assistant, how are you?"
    assert utterance.confidence == 0.95


def test_new_utterance_starts_after_reset() -> None:
    manager = UtteranceManager()

    first = manager.process(
        TranscriptionResult(
            transcript="Hello Assistant",
            is_final=True,
            speech_final=True,
            confidence=0.95,
        )
    )

    assert first is not None
    assert first.text == "Hello Assistant"

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
            transcript="Hello Assistant",
            is_final=False,
            speech_final=False,
            confidence=0.90,
        )
    )

    utterance = manager.process(
        TranscriptionResult(
            transcript="Hello Assistant, how are you?",
            is_final=True,
            speech_final=True,
            confidence=0.95,
        )
    )

    assert utterance is not None
    assert utterance.text == "Hello Assistant, how are you?"
    assert utterance.confidence == 0.95
