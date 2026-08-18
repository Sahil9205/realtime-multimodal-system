"""
Tests for the minimal Pipecat realtime pipeline.
"""

from app.realtime.pipeline import (
    PassthroughProcessor,
    create_pipeline,
    create_pipeline_worker,
)


def test_create_pipecat_pipeline() -> None:
    pipeline = create_pipeline()

    assert pipeline is not None

    processors = pipeline._processors

    assert len(processors) == 3
    assert isinstance(
        processors[1],
        PassthroughProcessor,
    )


def test_create_pipecat_pipeline_worker() -> None:
    worker = create_pipeline_worker()

    assert worker is not None