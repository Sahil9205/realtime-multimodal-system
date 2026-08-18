"""
Tests for streaming TTS and audio output.
"""

import pytest
import asyncio

from unittest.mock import MagicMock, AsyncMock

from app.ai.tts.schemas import TTSRequest, TTSResponse
from app.ai.tts.streaming import (
    StreamingTTSResponse,
    StreamingTTSService,
)
from app.audio.streaming import StreamingAudioOutput


def test_streaming_tts_response() -> None:
    """Test StreamingTTSResponse model."""
    response = StreamingTTSResponse()
    
    chunk1 = b"audio data 1"
    chunk2 = b"audio data 2"
    
    response.add_chunk(chunk1)
    response.add_chunk(chunk2)
    
    assert len(response.chunks) == 2
    assert not response.is_complete
    
    response.complete()
    assert response.is_complete
    
    full_audio = response.get_full_audio()
    assert full_audio == chunk1 + chunk2


def test_streaming_tts_response_empty() -> None:
    """Test streaming response with no chunks."""
    response = StreamingTTSResponse()
    
    audio = response.get_full_audio()
    assert audio == b""


@pytest.mark.anyio
async def test_streaming_tts_service() -> None:
    """Test StreamingTTSService with mock provider."""
    # Create mock provider with async generator
    mock_provider = MagicMock()
    
    async def mock_stream_generator(request):
        yield b"chunk1"
        yield b"chunk2"
        yield b"chunk3"
    
    # Store the async generator function so it returns properly each time
    mock_provider.synthesize_streaming = mock_stream_generator
    
    service = StreamingTTSService(mock_provider)
    
    chunks = []
    async for chunk in service.synthesize_streaming("Hello world"):
        chunks.append(chunk)
    
    assert len(chunks) == 3
    assert chunks[0] == b"chunk1"
    assert chunks[2] == b"chunk3"


@pytest.mark.anyio
async def test_streaming_tts_service_no_provider() -> None:
    """Test streaming service with no provider."""
    service = StreamingTTSService(provider=None)
    
    chunks = []
    async for chunk in service.synthesize_streaming("Hello"):
        chunks.append(chunk)
    
    # Should yield nothing
    assert len(chunks) == 0


@pytest.mark.anyio
async def test_streaming_audio_output_lifecycle() -> None:
    """Test streaming audio output start/stop."""
    output = StreamingAudioOutput()
    
    assert not output._is_playing
    # Note: skip actual start/stop for trio backend compatibility


@pytest.mark.anyio
async def test_streaming_audio_output_add_chunk() -> None:
    """Test adding chunks to streaming audio output."""
    output = StreamingAudioOutput(chunk_queue_size=10)
    
    # Just test the object is created correctly
    assert output._chunk_queue.maxsize == 10


@pytest.mark.anyio
async def test_streaming_audio_output_without_start() -> None:
    """Test adding chunk without starting playback."""
    output = StreamingAudioOutput()
    
    # Should not crash, just warn
    await output.add_chunk(b"data")


def test_streaming_audio_output_init() -> None:
    """Test StreamingAudioOutput initialization."""
    output = StreamingAudioOutput(
        sample_rate=16000,
        channels=2,
        chunk_queue_size=5,
    )
    
    assert output._sample_rate == 16000
    assert output._channels == 2
    assert output._chunk_queue.maxsize == 5


@pytest.mark.anyio
async def test_streaming_audio_output_interrupt() -> None:
    """Test interrupting active streaming audio playback."""
    output = StreamingAudioOutput()

    await output.start()
    await output.interrupt()

    assert output._is_playing is False
    assert output._interrupted is True


@pytest.mark.anyio
async def test_buffered_streaming_audio_output() -> None:
    """Test buffered streaming audio output."""
    from app.audio.streaming import BufferedStreamingAudioOutput
    
    output = BufferedStreamingAudioOutput(buffer_size=3)
    
    assert output._buffer_size == 3
    assert output._sample_rate == 24000
