"""
Custom exceptions for the application.
"""


class VoiceAssistantError(Exception):
    """
    Base exception for the application.
    """


class AudioError(VoiceAssistantError):
    """
    Raised when an audio-related operation fails.
    """


class ASRError(VoiceAssistantError):
    """
    Raised when speech-to-text fails.
    """


class LLMError(VoiceAssistantError):
    """
    Raised when the language model fails.
    """


class TTSError(VoiceAssistantError):
    """
    Raised when text-to-speech fails.
    """


class PipelineError(VoiceAssistantError):
    """
    Raised when the orchestration pipeline fails.
    """


class WebSocketError(VoiceAssistantError):
    """
    Raised when a websocket operation fails.
    """


class TimeoutError(VoiceAssistantError):
    """
    Raised when an operation exceeds the allowed timeout.
    """


class ConfigurationError(VoiceAssistantError):
    """
    Raised when application configuration is invalid.
    """


