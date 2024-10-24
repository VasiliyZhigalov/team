import asyncio
from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentId, AgentProxy
from autogen_core.components.models import UserMessage

import llm_client

from planning.coder import Coder
from planning.orchestrator import Orchestrator
from messages import BroadcastMessage


async def main() -> None:
    runtime = SingleThreadedAgentRuntime()
    coder = await Coder.register(
        runtime,
        "coder",
        lambda: Coder(
            model_client=llm_client.client_gpt_4o_mini
        )
    )
    coder = AgentProxy(AgentId("coder", "default"), runtime)
    await Orchestrator.register(
        runtime,
        "orchestrator",
        lambda: Orchestrator(
            model_client=llm_client.client,
            agents=[coder, ]

        )
    )
    runtime.start()
    orchestrator_id = AgentId("orchestrator", "default")
    task = '''
    Необходимо написать игру шахматы.
    '''
    result = await runtime.send_message(BroadcastMessage(content=UserMessage(task, source="user")), orchestrator_id)
    await runtime.stop_when_idle()


if __name__ == "__main__":
    asyncio.run(main())
