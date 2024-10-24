import json
import pprint
from typing import List
import streamlit_chat
import streamlit as st

from autogen_core.base import MessageContext, AgentProxy, TopicId
from autogen_core.components import default_subscription
from autogen_core.components.models import UserMessage, ChatCompletionClient, LLMMessage

from messages import BroadcastMessage, RequestReplyMessage
from planning.base_agent import BaseAgent

from .orchestrator_prompts import (
    ORCHESTRATOR_PLAN_PROMPT, ORCHESTRATOR_SUBTASK_EXECUTE_PROMPT, ORCHESTRATOR_SUMMARY_PROMPT
)
from .output_message import get_plan, get_subtask_to_worker


@default_subscription
class Orchestrator(BaseAgent):
    def __init__(self, model_client: ChatCompletionClient,
                 agents: List[AgentProxy] = []):
        super().__init__("A planning and orchestrator agent")
        self._model_client = model_client
        self.agents = agents
        self.task = ''
        self.plan = ''
        self.summary = ''
        self._chat_history: List[LLMMessage] = []

    async def _handle_broadcast(self, message: BroadcastMessage, ctx: MessageContext) -> None:
        content = message.content.content
        self._chat_history.append(message.content)
        # Создаем план
        if len(self.task) == 0:
            self.task = content
            await self.create_plan(self.task)
            return await self._handle_broadcast(message, ctx)
        # Идем по плану.
        for substask in self.plan["subtasks"]:
            if substask["status"] == "not_started":
                next_subtask = substask
                for agent in self.agents:
                    if (await agent.metadata)["type"] == next_subtask["executor"]:
                        msg = ORCHESTRATOR_SUBTASK_EXECUTE_PROMPT.format(
                            task=self.task,
                            description=self.plan['analysis'],
                            subtask=next_subtask['name'],
                            steps='\n'.join(map(str, next_subtask['steps']))
                        )
                        user_message = UserMessage(content=msg, source=self.metadata["type"])
                        topic_id = TopicId("default", self.id.key)
                        await self.publish_message(
                            BroadcastMessage(content=user_message, request_halt=False),
                            topic_id=topic_id,
                        )
                        print(f'{'-' * 80}\nOrchestrator. Текущая задача для {agent.id}\n {msg}')
                        with st.chat_message("ai"):
                            st.text(self.metadata["type"]+'->'+next_subtask["executor"])
                            st.markdown(get_subtask_to_worker(next_subtask["executor"], next_subtask['name'],
                                                              next_subtask['steps']))
                        substask["status"] = "in_progress"
                        request_reply_message = RequestReplyMessage()
                        await self.send_message(request_reply_message, agent.id)
                        return
        prompt = ORCHESTRATOR_SUMMARY_PROMPT.format(task=self.task)
        response = await self._model_client.create(self._chat_history + [UserMessage(prompt, source="user")],
                                                   json_output=True)
        self.summary = response.content
        with st.chat_message("ai"):
            st.text(self.metadata["type"])
            st.markdown(self.summary)
        st.session_state.summary = self.summary

    async def create_plan(self, task):
        try:
            print(task)
            names = [(await a.metadata)['type'] for a in self.agents]
            prompt = ORCHESTRATOR_PLAN_PROMPT.format(task=task, team=await self.get_team_description(), names=names)
            response = await self._model_client.create([UserMessage(prompt, source="user")], json_output=True)
            self.plan = json.loads(response.content)
            plan = get_plan(self.plan)
            with st.chat_message("ai"):
                st.text(self.metadata["type"])
                st.markdown(plan)

            st.session_state.plan = plan
            pprint.pprint(f'{'-' * 80}\nOrchestrator.\n {plan}')

        except:
            self.logger.error(
                "Ошибка формирования json"
            )
            await self.create_plan(task)

    async def get_team_description(self) -> str:
        # a single string description of all agents in the team
        team_description = ""
        for agent in self.agents:
            metadata = await agent.metadata
            name = metadata["type"]
            description = metadata["description"]
            team_description += f"{name}: {description}\n"
        return team_description
