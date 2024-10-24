from typing import List

import streamlit_chat
import streamlit as st
from autogen_core.base import MessageContext, TopicId
from autogen_core.components import default_subscription
from autogen_core.components.models import LLMMessage, UserMessage, SystemMessage, AssistantMessage
from planning.base_agent import BaseAgent
from messages import BroadcastMessage

DEFAULT_DESCRIPTION = "A helpful and general-purpose AI assistant that has strong language skills, Python skills, and Linux command line skills."

DEFAULT_SYSTEM_MESSAGES = [
    SystemMessage("""You are a helpful AI assistant.
Solve tasks using your coding and language skills.
In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.
    1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
    2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
Reply "TERMINATE" in the end when everything is done. РЕЗУЛЬТАТЫ ПИШИ НА РУССКОМ ЯЗЫКЕ""")
]


@default_subscription
class Coder(BaseAgent):
    def __init__(self, model_client):
        super().__init__(description=DEFAULT_DESCRIPTION),
        self.model_client = model_client
        self._chat_history: List[LLMMessage] = []
        self.system_messages = DEFAULT_SYSTEM_MESSAGES

    async def _handle_broadcast(self, message: BroadcastMessage, cxt: MessageContext):
        self._chat_history.append(message.content)

    async def _handle_request_reply(self, message, ctx):
        response = await self.model_client.create(self.system_messages + self._chat_history)
        assistant_message = AssistantMessage(content=response.content, source=self.metadata["type"])
        self._chat_history.append(assistant_message)
        user_message = UserMessage(content=response.content, source=self.metadata["type"])
        topic_id = TopicId("default", self.id.key)
        await self.publish_message(
            BroadcastMessage(content=user_message),
            topic_id=topic_id,
        )
        with st.chat_message("ai"):
            st.text(self.metadata["type"])
            st.markdown(user_message.content)
        print(f'{'-' * 80}\nCoder. Ответ: {user_message.content}')
