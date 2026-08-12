"""
Application configuration.

Loads and validates all environment variables using Pydantic Settings.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    """

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    APP_NAME: str = "Voice Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ------------------------------------------------------------------
    # API Keys
    # ------------------------------------------------------------------
    DEEPGRAM_API_KEY: str = Field(default="")
    

    # ------------------------------------------------------------------
    # LLM
    # ------------------------------------------------------------------
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4.1-mini"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 512

    # ------------------------------------------------------------------
    # Audio
    # ------------------------------------------------------------------
    SAMPLE_RATE: int = 16000
    CHANNELS: int = 1
    CHUNK_SIZE: int = 1024
    AUDIO_INPUT_DEVICE: int =2

    # ------------------------------------------------------------------
    # Timeouts (seconds)
    # ------------------------------------------------------------------
    ASR_TIMEOUT: int = 10
    LLM_TIMEOUT: int = 30
    TTS_TIMEOUT: int = 15

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.
    """
    return Settings()


settings = get_settings()
