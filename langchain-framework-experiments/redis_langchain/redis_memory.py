import os
from dotenv import load_dotenv
load_dotenv()

import redis
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import (
    BaseChatMessageHistory,
)
from langchain_redis import RedisChatMessageHistory

model = ChatOpenAI(model="gpt-4.1-nano", api_key=os.getenv("OPENAI_API_KEY"))

human_template = f"{{question}}"
prompt_template = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="history"),
        ("human", human_template),
    ]
)
chain = prompt_template | model


redis_client = redis.Redis(host="localhost", port=6379)


def get_redis_history(session_id: str) -> BaseChatMessageHistory:
    return RedisChatMessageHistory(session_id=session_id, redis_client=redis_client)


chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history=get_redis_history,
    input_messages_key="question",
    history_messages_key="history",
)

while True:
    user_question = input(">>>>")
    result = chain_with_history.invoke(
        {"question": user_question},
        config={"configurable": {"session_id": "session_1"}},
    )
    print(result.content)