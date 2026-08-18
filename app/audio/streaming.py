"""
Streaming audio output for real-time playback.
"""

from __future__ import annotations

import asyncio
import io

from pydub import AudioSegment
import sounddevice as sd

from app.core.logging import get_logger


logger = get_logger(__name__)


class StreamingAudioOutput:
    """
    Handles streaming audio playback in real-time.
    
    Allows audio to be played as chunks arrive instead of
    waiting for the complete audio.
    """

    def __init__(
        self,
        sample_rate: int = 24000,
        channels: int = 1,
        chunk_queue_size: int = 10,
    ) -> None:
        """
        Initialize streaming audio output.

        Args:
            sample_rate: Audio sample rate.
            channels: Number of audio channels.
            chunk_queue_size: Max size of chunk queue.
        """
        self._sample_rate = sample_rate
        self._channels = channels
        self._chunk_queue: asyncio.Queue = asyncio.Queue(chunk_queue_size)
        self._playback_task: asyncio.Task | None = None
        self._stream = None
        self._is_playing = False
        self._interrupted = False

        logger.info(
            "StreamingAudioOutput initialized: "
            "sample_rate=%d, channels=%d",
            sample_rate,
            channels,
        )

    async def start(self) -> None:
        """Start the playback task."""
        if self._is_playing:
            logger.warning("Audio playback already started.")
            return

        self._interrupted = False
        self._is_playing = True

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.warning(
                "No running asyncio loop; deferring playback scheduling."
            )
            return

        self._playback_task = loop.create_task(self._playback_loop())

        logger.info("Audio playback started.")

    async def stop(self) -> None:
        """Stop the playback task."""
        if not self._is_playing:
            return

        self._is_playing = False
        self._interrupted = False

        # Send stop signal
        await self._chunk_queue.put(None)

        # Wait for playback to complete
        if self._playback_task:
            try:
                await asyncio.wait_for(
                    self._playback_task,
                    timeout=5.0,
                )
            except asyncio.TimeoutError:
                logger.warning("Playback task timed out during stop.")
            finally:
                self._playback_task = None

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        logger.info("Audio playback stopped.")

    async def interrupt(self) -> None:
        """Stop active playback immediately for barge-in handling."""
        self._interrupted = True
        self._is_playing = False

        if self._playback_task is not None:
            self._playback_task.cancel()
            self._playback_task = None

        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        while not self._chunk_queue.empty():
            try:
                self._chunk_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        logger.info("Audio playback interrupted.")

    async def add_chunk(self, chunk: bytes) -> None:
        """
        Add an audio chunk for playback.

        Args:
            chunk: Audio bytes to play.
        """
        if not self._is_playing:
            logger.warning("Playback not started, ignoring chunk.")
            return

        try:
            await asyncio.wait_for(
                self._chunk_queue.put(chunk),
                timeout=1.0,
            )
            logger.debug(
                "Added audio chunk: %d bytes",
                len(chunk),
            )
        except asyncio.TimeoutError:
            logger.warning("Chunk queue full, dropping chunk.")

    async def _playback_loop(self) -> None:
        """Process and play audio chunks."""
        try:
            logger.info("Playback loop started.")

            while True:
                chunk = await self._chunk_queue.get()

                if chunk is None:
                    # Stop signal received
                    logger.info("Stop signal received in playback loop.")
                    break

                if not chunk:
                    # Empty chunk, skip
                    continue

                await self._play_chunk(chunk)

        except Exception as exc:
            logger.error(
                "Error in playback loop: %s",
                exc,
                exc_info=True,
            )
        finally:
            logger.info("Playback loop ended.")

    async def _play_chunk(self, chunk: bytes) -> None:
        """
        Play a single audio chunk.

        Args:
            chunk: Audio bytes to play.
        """
        try:
            audio = AudioSegment.from_file(
                io.BytesIO(chunk),
                format="mp3",
            )

            samples = audio.get_array_of_samples()

            # Run audio playback in executor to avoid blocking
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                lambda: sd.play(
                    samples,
                    samplerate=audio.frame_rate,
                    blocking=True,
                ),
            )

            logger.debug(
                "Played audio chunk: %d samples",
                len(samples),
            )

        except Exception as exc:
            logger.error(
                "Error playing chunk: %s",
                exc,
                exc_info=True,
            )


class BufferedStreamingAudioOutput(StreamingAudioOutput):
    """
    Streaming audio output with buffering for smooth playback.
    
    Buffers multiple chunks before playback to handle
    inconsistent chunk delivery.
    """

    def __init__(
        self,
        sample_rate: int = 24000,
        channels: int = 1,
        buffer_size: int = 5,
        chunk_queue_size: int = 20,
    ) -> None:
        """
        Initialize buffered streaming audio output.

        Args:
            sample_rate: Audio sample rate.
            channels: Number of audio channels.
            buffer_size: Number of chunks to buffer before playback.
            chunk_queue_size: Max size of chunk queue.
        """
        super().__init__(sample_rate, channels, chunk_queue_size)
        self._buffer_size = buffer_size
        self._chunk_buffer: list[bytes] = []

        logger.info(
            "BufferedStreamingAudioOutput initialized: "
            "buffer_size=%d",
            buffer_size,
        )

    async def _playback_loop(self) -> None:
        """Process chunks with buffering."""
        try:
            logger.info("Buffered playback loop started.")

            while True:
                chunk = await self._chunk_queue.get()

                if chunk is None:
                    # Stop signal - flush remaining chunks
                    logger.info("Stop signal received, flushing buffer.")
                    if self._chunk_buffer:
                        combined = b"".join(self._chunk_buffer)
                        await self._play_chunk(combined)
                    break

                if not chunk:
                    continue

                self._chunk_buffer.append(chunk)

                if len(self._chunk_buffer) >= self._buffer_size:
                    combined = b"".join(self._chunk_buffer)
                    await self._play_chunk(combined)
                    self._chunk_buffer.clear()

        except Exception as exc:
            logger.error(
                "Error in buffered playback loop: %s",
                exc,
                exc_info=True,
            )
        finally:
            logger.info("Buffered playback loop ended.")
