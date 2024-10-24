import asyncio

from autogen_core.components.models import OpenAIChatCompletionClient, UserMessage

client = OpenAIChatCompletionClient(
    model="gpt-4o",
    base_url="http://localhost:1337/v1",
    api_key="123"
)
client_gpt_4o_mini = OpenAIChatCompletionClient(
    model="gpt-4o-mini",
    base_url="http://localhost:1337/v1",
    api_key="123"
)
