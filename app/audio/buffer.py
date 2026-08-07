"""
Audio buffer implementation.
"""

from __future__ import annotations

import asyncio

from app.audio.schemas import AudioChunk


class AudioBuffer:
    """
    Asynchronous buffer for audio chunks.
    """

    def __init__(self, maxsize: int = 100) -> None:
        """
        Initialize the audio buffer.

        Args:
            maxsize: Maximum number of audio chunks.
        """
        self._queue: asyncio.Queue[AudioChunk] = asyncio.Queue(
            maxsize=maxsize,
        )

    async def put(self, chunk: AudioChunk) -> None:
        """
        Add an audio chunk to the buffer.
        """
        await self._queue.put(chunk)

    async def get(self) -> AudioChunk:
        """
        Get the next audio chunk.
        """
        return await self._queue.get()

    def empty(self) -> bool:
        """
        Return True if the buffer is empty.
        """
        return self._queue.empty()

    def full(self) -> bool:
        """
        Return True if the buffer is full.
        """
        return self._queue.full()

    def size(self) -> int:
        """
        Return the current buffer size.
        """
        return self._queue.qsize()

    async def clear(self) -> None:
        """
        Remove all audio chunks from the buffer.
        """
        while not self._queue.empty():
            self._queue.get_nowait()
            self._queue.task_done()