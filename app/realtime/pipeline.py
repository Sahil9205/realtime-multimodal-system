"""
Minimal Pipecat real-time pipeline.

This module is intentionally small.
It establishes the application's Pipecat
orchestration boundary before adding
transport, ASR, LLM, and TTS.
"""

from __future__ import annotations

from pipecat.frames.frames import Frame
from pipecat.processors.frame_processor import (
    FrameDirection,
    FrameProcessor,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineWorker
from pipecat.workers.runner import WorkerRunner


class PassthroughProcessor(FrameProcessor):
    """
    Minimal processor that forwards every frame unchanged.
    """

    async def process_frame(
        self,
        frame: Frame,
        direction: FrameDirection,
    ) -> None:
        await super().process_frame(frame, direction)

        await self.push_frame(
            frame,
            direction,
        )


def create_pipeline() -> Pipeline:
    """
    Create the application's initial Pipecat pipeline.
    """

    processor = PassthroughProcessor()

    return Pipeline(
        processors=[
            processor,
        ],
    )


def create_pipeline_worker() -> PipelineWorker:
    """
    Create a PipelineWorker around the application pipeline.
    """

    pipeline = create_pipeline()

    return PipelineWorker(
        pipeline,
    )


async def run_pipeline() -> None:
    """
    Run the Pipecat pipeline worker.
    """


    worker = create_pipeline_worker()


    runner = WorkerRunner()


    await runner.add_workers(worker)
    await runner.run()
