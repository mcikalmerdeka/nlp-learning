import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent

# Setup a basic weather database in dictionary
weather_db = {
    "Tokyo": "Sunny",
    "New York": "Rainy",
    "London": "Cloudy",
    "Sydney": "Sunny",
    "Beijing": "Cloudy",
}

temperature_db = {
    "Tokyo": "25",
    "New York": "15",
    "London": "10",
    "Sydney": "25",
    "Beijing": "10",
}

# Initialize Tools
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a specified city."""

    # Simulate API call
    return f"It's always {weather_db.get(city, 'unknown')} in {city}!"

@tool
def get_temperature(city: str) -> str:
    """Get the current temperature for a specified city."""

    # Simulate API call
    return f"It's always {temperature_db.get(city, 'unknown')}°C in {city}!"

tools = [get_weather, get_temperature]

# Initialize Model and Agent
llm = ChatOpenAI(model="gpt-4o-mini",
                 openai_api_key=os.getenv("OPENAI_API_KEY"),
                 temperature=0.5,
                 max_tokens=250)

agent = create_agent(
    llm,                    # LLM with tool calling support
    tools,                  # List of tools
    system_prompt="You are a helpful assistant with access to tools."
)

# # Running option 1: Invoke the Agent
# result = agent.invoke({
#     "messages": [{"role": "user", "content": "What's the weather and temperature in New York and Tokyo?"}]
# })

# print(result["messages"][-1].content)

# Running option 2: Streaming response
for chunk in agent.stream({
    "messages": [{"role": "user", "content": "What's the weather and temperature in New York and Tokyo?"}]
}, stream_mode="values"):
    if "messages" in chunk:
        last_msg = chunk["messages"][-1]
        if last_msg.content:
            print(last_msg.content, end="", flush=True)