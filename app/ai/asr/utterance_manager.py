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
        self._finalized_text = ""
        self._confidence: float | None = None

    def process(
        self,
        result: TranscriptionResult,
        force_finalize: bool = False,
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

        # Interim results replace the current hypothesis. Final segments can
        # arrive several times before speech_final, so preserve each segment
        # and combine them when the user ends the turn.
        self._current_text = transcript
        self._confidence = result.confidence

        if result.is_final:
            self._finalized_text = " ".join(
                part
                for part in (self._finalized_text, transcript)
                if part
            )

        logger.debug(
            "Updated utterance state: text=%r confidence=%s",
            self._current_text,
            self._confidence,
        )

        # ``is_final`` only finalizes a speech segment. Wait for Deepgram's
        # endpoint detector to mark the complete speech turn; otherwise the
        # assistant responds to partial phrases.
        if not result.speech_final and not force_finalize:
            return None

        utterance = UserUtterance(
            text=self._finalized_text or self._current_text,
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
        self._finalized_text = ""
        self._confidence = None
