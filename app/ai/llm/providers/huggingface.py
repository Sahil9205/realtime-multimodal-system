"""
Hugging Face LLM provider.
"""

from __future__ import annotations
import asyncio

from huggingface_hub import InferenceClient
from app.ai.llm.base import BaseLLM
from app.ai.llm.schemas import LLMRequest, LLMResponse
from app.core.logging import get_logger
from app.core.config import settings


logger = get_logger(__name__)


class HuggingFaceLLM(BaseLLM):
    """
    Hugging Face implementation of the LLM provider.

    Model initialization/inference will be connected later.
    """
    def __init__(self):
        if not settings.HF_TOKEN:
            raise ValueError(
                "HF_TOKEN is not configured."
            )

        self._client = InferenceClient(
            api_key=settings.HF_TOKEN,
        )

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a response from the Hugging Face model.

        Falls back to a deterministic local response when the configured
        inference model is unavailable or unsupported by the current
        provider access settings.
        """

        model_name = settings.LLM_MODEL_NAME or "Qwen/Qwen2.5-7B-Instruct"

        logger.info(
            "Generating response with Hugging Face model: %s",
            model_name,
        )

        messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in request.messages
        ]

        try:
            # The SDK method is synchronous. Run it outside the event loop so
            # a user interruption can cancel the awaiting voice turn.
            response = await asyncio.to_thread(
                self._client.chat.completions.create,
                model=model_name,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            choice = response.choices[0]
            content = choice.message.content

            if not content:
                raise RuntimeError(
                    "Hugging Face returned an empty response."
                )

            logger.info(
                "Hugging Face response generated: %r",
                content,
            )

            usage = None

            if response.usage is not None:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            return LLMResponse(
                content=str(content),
                model="huggingface",
                finish_reason="stop",
                usage=usage,
            )

        except Exception as exc:
            logger.warning(
                "Hugging Face generation failed for model %s: %s. "
                "Using deterministic fallback response.",
                model_name,
                exc,
            )

            # Never expose the internal prompt or conversation history to the
            # user. It is intended only for the model and may be spoken by
            # TTS when a provider is unavailable.
            fallback_content = (
                "I'm sorry, I can't reach the language model right now. "
                "Please try again in a moment."
            )

            return LLMResponse(
                content=fallback_content,
                model="huggingface-fallback",
                finish_reason="fallback",
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            )
