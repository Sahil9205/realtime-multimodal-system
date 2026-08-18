"""
Core conversation engine.
"""

from __future__ import annotations

from app.ai.asr.schemas import UserUtterance

from app.conversation.handlers.general import GeneralConversationHandler
from app.conversation.handlers.greeting import GreetingHandler
from app.conversation.handlers.information import InformationRequestHandler

from app.conversation.intent.classifier import IntentClassifier
from app.conversation.intent.router import IntentRouter

from app.conversation.memory import ConversationMemory
from app.conversation.schemas.conversation_input import ConversationInput
from app.conversation.schemas.conversation_output import ConversationOutput

from app.conversation.response.manager import ResponseManager
from app.ai.llm.manager import LLMManager

from app.ai.llm.service import LLMService

from app.core.logging import get_logger


logger = get_logger(__name__)


class ConversationEngine:
    """
    Coordinates processing of user utterances.

    The engine currently provides the boundary between
    the voice pipeline and future conversation logic such
    as intent detection, memory, RAG, and LLM generation.

    Flow:

        UserUtterance
            ↓
        ConversationInput
            ↓
        IntentClassifier
            ↓
        IntentRouter
            ↓
        ConversationHandler
            ↓
        ConversationOutput
    """

    def __init__(
        self,
        classifier: IntentClassifier | None = None,
        router: IntentRouter | None = None,
        response_manager: ResponseManager | None = None,
        llm_manager: LLMManager | None = None,
        llm_service: LLMService | None = None,
        memory: ConversationMemory | None = None,
    ) -> None:

        self._response_manager = (
            response_manager
            if response_manager is not None
            else ResponseManager()
        )

        self._llm_manager = (
        llm_manager
        if llm_manager is not None
        else LLMManager()
        )

        self._llm_service = (
        llm_service
        if llm_service is not None
        else LLMService()
        )

        self._classifier = (
            classifier
            if classifier is not None
            else IntentClassifier()
        )

        self._router = (
            router
            if router is not None
            else IntentRouter(
                greeting_handler=GreetingHandler(),
                information_handler=InformationRequestHandler(),
                general_handler=GeneralConversationHandler(),
            )
        )

        self._memory = (
            memory
            if memory is not None
            else ConversationMemory()
        )

        logger.info("ConversationEngine initialized with memory support.")

    async def process(
        self,
        utterance: UserUtterance,
        ) -> ConversationOutput:
        """
        Process a completed user utterance.

        Flow:
            UserUtterance
                ↓
            ConversationMemory.add_user_message()
                ↓
            ConversationInput
                ↓
            IntentClassifier
                ↓
            IntentRouter
                ↓
            ConversationHandler
                ↓
            LLMService (with memory context)
                ↓
            ResponseManager
                ↓
            ConversationMemory.add_assistant_message()
                ↓
            ConversationOutput
        """

        # Store user message in memory
        self._memory.add_user_message(utterance.text)

        conversation_input = ConversationInput(
            text=utterance.text,
            confidence=utterance.confidence,
        )

        logger.info(
            "Processing conversation input: %r",
            conversation_input.text,
        )

        intent = self._classifier.classify(
            conversation_input.text
        )

        logger.info(
            "Conversation intent detected: %s",
            intent.value,
        )

        response = self._router.route(
            intent,
            conversation_input,
        )

        # Get recent conversation context for LLM
        memory_context = self._memory.get_context_string(num_messages=6)
        
        context_prompt = response.text
        if memory_context:
            context_prompt = (
                f"Previous conversation context:\n{memory_context}\n\n"
                f"New request: {response.text}"
            )

        llm_response = await self._llm_service.generate(
            context_prompt,
        )

        final_response = self._response_manager.create(
            llm_response.content,
        )

        # Store assistant message in memory
        self._memory.add_assistant_message(final_response.text)

        logger.info(
            "Conversation response generated: %r",
            final_response.text,
        )

        return final_response

    def get_memory(self) -> ConversationMemory:
        """
        Get the conversation memory instance.

        Returns:
            The ConversationMemory object.
        """
        return self._memory

    def clear_memory(self) -> None:
        """
        Clear all conversation memory.
        """
        self._memory.clear()