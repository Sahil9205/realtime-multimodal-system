"""
User utterance management for streaming ASR.
"""

from __future__ import annotations

from app.ai.asr.schemas import (
    TranscriptionResult,
    UserUtterance,
)
from app.core.logging import get_logger


logger = get_logger(__name__)


class UtteranceManager:
    """
    Converts streaming transcription results into complete
    user utterances.
    """

    def __init__(self) -> None:
        self._current_text = ""
        self._confidence: float | None = None

    def process(
        self,
        result: TranscriptionResult,
    ) -> UserUtterance | None:
        """
        Process one transcription result.

        Interim results update the current speech state.

        A speech-final result produces a complete UserUtterance.

        Args:
            result: Transcription result from the ASR provider.

        Returns:
            A completed UserUtterance when the speech segment ends,
            otherwise None.
        """

        transcript = result.transcript.strip()

        if not transcript:
            return None

        # Deepgram's streaming transcript represents the current
        # hypothesis, rather than a new piece of text to append.
        self._current_text = transcript
        self._confidence = result.confidence

        logger.debug(
            "Updated utterance state: text=%r confidence=%s",
            self._current_text,
            self._confidence,
        )

        if not result.speech_final:
            return None

        utterance = UserUtterance(
            text=self._current_text,
            confidence=self._confidence,
        )

        logger.info(
            "User utterance completed: %r",
            utterance.text,
        )

        self.reset()

        return utterance

    def reset(self) -> None:
        """
        Reset the current utterance state.
        """

        self._current_text = ""
        self._confidence = None