import logging
from typing import List

from autogen_core.base import MessageContext
from autogen_core.components import RoutedAgent, message_handler
from autogen_core.components.models import LLMMessage
from autogen_core.application.logging import EVENT_LOGGER_NAME

from messages import BroadcastMessage, ResetMessage, DeactivateMessage, RequestReplyMessage, AgentEvent, TaskMessage


class BaseAgent(RoutedAgent):
    def __init__(self, description):
        super().__init__(description=description)
        self.chat_history: List[LLMMessage] =[]
        self.logger = logging.getLogger(EVENT_LOGGER_NAME + f".{self.id.key}.agent")


    @message_handler
    async def handle_message(
            self,
            message: BroadcastMessage | ResetMessage | DeactivateMessage | RequestReplyMessage | TaskMessage,
            ctx: MessageContext,
    ) -> None:
        if isinstance(message, RequestReplyMessage):
            await self._handle_request_reply(message, ctx)

        elif isinstance(message, TaskMessage):
            await self._handle_task(message, ctx)

        elif isinstance(message, BroadcastMessage):
            await self._handle_broadcast(message, ctx)

        elif isinstance(message, ResetMessage):
            await self._handle_reset(message, ctx)
        elif isinstance(message, DeactivateMessage):
            await self._handle_deactivate(message, ctx)

    async def _handle_broadcast(self, message: BroadcastMessage, ctx: MessageContext) -> None:
        raise NotImplementedError()

    async def _handle_reset(self, message: ResetMessage, ctx: MessageContext) -> None:
        raise NotImplementedError()

    async def _handle_request_reply(self, message: RequestReplyMessage, ctx: MessageContext) -> None:
        raise NotImplementedError()

    async def _handle_task(self, message: TaskMessage, ctx: MessageContext) -> None:
        raise NotImplementedError()

    async def _handle_deactivate(self, message: DeactivateMessage, ctx: MessageContext) -> None:
        """Handle a deactivate message."""
        self._enabled = False
        self.logger.info(
            AgentEvent(
                f"{self.metadata['type']} (deactivated)",
                "",
            )
        )
