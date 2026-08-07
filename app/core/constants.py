"""
Application constants.
"""

from enum import Enum


class AudioFormat(str, Enum):
    """
    Supported audio formats.
    """

    PCM = "pcm"
    WAV = "wav"


class AudioEncoding(str, Enum):
    """
    Supported audio encodings.
    """

    LINEAR16 = "linear16"


class LogMessage:
    """
    Common log messages.
    """

    APPLICATION_STARTED = "Application started."
    APPLICATION_STOPPED = "Application stopped."

    ASR_CONNECTED = "ASR provider connected."
    ASR_DISCONNECTED = "ASR provider disconnected."

    LLM_CONNECTED = "LLM provider connected."

    TTS_CONNECTED = "TTS provider connected."

    WEBSOCKET_CONNECTED = "WebSocket connected."
    WEBSOCKET_DISCONNECTED = "WebSocket disconnected."


class Event:
    """
    Common event names.
    """

    SPEECH_STARTED = "speech_started"
    SPEECH_ENDED = "speech_ended"

    TRANSCRIPT_RECEIVED = "transcript_received"

    RESPONSE_GENERATED = "response_generated"

    AUDIO_STARTED = "audio_started"
    AUDIO_COMPLETED = "audio_completed"