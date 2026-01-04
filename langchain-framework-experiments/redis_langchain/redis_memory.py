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

# Initialize the llm
model = ChatOpenAI(model="gpt-4.1-nano", api_key=os.getenv("OPENAI_API_KEY"))

# Define the prompt template
human_template = f"{{question}}"
prompt_template = ChatPromptTemplate.from_messages(
    [
        # Add the history to the prompt
        MessagesPlaceholder(variable_name="history"),
        # Add the human message to the prompt
        ("human", human_template),
    ]
)

# Define the chain
chain = prompt_template | model

# Initialize the redis client
redis_client = redis.Redis(host="localhost", port=6379, db=0) # specify the database number (default is 0)

# Define the function to get the redis history
def get_redis_history(session_id: str) -> BaseChatMessageHistory:
    return RedisChatMessageHistory(session_id=session_id, redis_client=redis_client)

# Define the chain with history from redis and the new query from the user
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history=get_redis_history,
    input_messages_key="question",
    history_messages_key="history",
)

# Define the main conversation loop
if __name__ == "__main__":
    while True:
        user_question = input(">>>>")
        result = chain_with_history.invoke(
            {"question": user_question},
            config={"configurable": {"session_id": "session_4"}}
        )
        print(result.content)