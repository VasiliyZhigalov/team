import asyncio

import streamlit as st
from streamlit_chat import message

import warnings

from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.base import AgentProxy, AgentId
from autogen_core.components.models import UserMessage

from messages import BroadcastMessage
from planning import llm_client
from planning.coder import Coder
from planning.orchestrator import Orchestrator

# запуск g4free
import threading
from g4f.api import run_api
import g4f


def start_server_g4f():
    g4f.debug.logging = True
    run_api()



warnings.filterwarnings('ignore')

# Инициализация состояния сессии
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'task' not in st.session_state:
    st.session_state.task = ""
if 'plan' not in st.session_state:
    st.session_state.plan = ""
if 'summary' not in st.session_state:
    st.session_state.summary = ""


# Функция для запуска агентов
async def run_agents(task):
    runtime = SingleThreadedAgentRuntime()
    coder = await Coder.register(
        runtime,
        "coder",
        lambda: Coder(model_client=llm_client.client)
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
    result = await runtime.send_message(BroadcastMessage(content=UserMessage(task, source="user")), orchestrator_id)
    await runtime.stop_when_idle()
    return result


# Основной интерфейс
st.set_page_config(
    page_title="Думатель",
    page_icon="🌟",
    layout="wide",  # Делает страницу широкой
    initial_sidebar_state="expanded"  # Разворачивает боковую панель
)
with st.spinner('Сервер g4f запущен...'):
    thread = threading.Thread(target=start_server_g4f)
    thread.start()

for sender, str_message in st.session_state.chat_history:
    if sender == 'user':
        message(str_message, is_user=True)
    else:
        message(str_message, is_user=False)

if chat_input := st.chat_input("Введите сообщение:"):
    with st.chat_message("user"):
        st.markdown(chat_input)
    st.session_state.chat_history.append(('user', chat_input))
    with st.spinner('Агенты работают над задачей...'):
        asyncio.run(run_agents(chat_input))

with st.sidebar:
    with st.expander("План"):
        text_container = st.empty()
        text_container.text_area("План", value=st.session_state.plan, height=600)

    text_container1 = st.empty()
    with text_container1.expander("Резюме"):
        user_input = st.text_area("Свод:", value=st.session_state.summary, height=600)
