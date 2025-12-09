"""
This script demonstrates the basic usage of LangChain framework. Several features are showcased:
1. Tool calling
2. Structured output
3. Agent creation
4. Streaming response
5. Memory
6. Multi-agent collaboration
"""

import os
import json
from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver


# Setup a basic weather database in dictionary
weather_db = {
    "Tokyo": "Sunny",
    "New York": "Rainy",
    "London": "Cloudy",
    "Sydney": "Sunny",
    "Beijing": "Cloudy",
}

temperature_db = {
    "Tokyo": 25,
    "New York": 15,
    "London": 10,
    "Sydney": 25,
    "Beijing": 10,
}

# Setup structured output for Research Agent
class WeatherReport(BaseModel):
    """Weather report for a specified city."""
    city: str = Field(..., description="The city of requested weather")
    weather: str = Field(..., description="The current weather on the specified city")
    temperature: int = Field(..., description="The current temperature on the specified city")

class WeatherReportList(BaseModel):
    """List of weather reports for multiple cities."""
    reports: list[WeatherReport] = Field(..., description="List of weather reports for each requested city")


# ============================================
# RESEARCH AGENT: Handles weather data lookup
# ============================================

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a specified city."""
    return weather_db.get(city, "unknown")

@tool
def get_temperature(city: str) -> int:
    """Get the current temperature for a specified city."""
    return temperature_db.get(city, 0)

weather_tools = [get_weather, get_temperature]

# Initialize Research Agent LLM
research_llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    max_tokens=500
)

# Research Agent: structured output, no memory (stateless)
research_agent = create_agent(
    research_llm,
    weather_tools,
    system_prompt="You are a weather research agent. Use the tools to look up weather and temperature for the requested cities. Return structured data for ALL cities mentioned.",
    response_format=WeatherReportList,
)


# ============================================
# CHAT AGENT: Conversational interface
# ============================================

@tool
def lookup_weather(cities: str) -> str:
    """
    Look up weather information for one or more cities.
    Pass a comma-separated list of city names, e.g., "Tokyo, New York".
    Returns structured weather data that you can use to form a natural response.
    """
    result = research_agent.invoke({
        "messages": [
            {"role": "user", "content": f"Get weather and temperature for: {cities}"}
        ]
    })
    return result["messages"][-1].content

chat_tools = [lookup_weather]

# Initialize memory for Chat Agent
chat_checkpointer = InMemorySaver()

# Chat Agent LLM
chat_llm = ChatOpenAI(
    model="gpt-4o-mini",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
    max_tokens=500
)

# Chat Agent: conversational, with memory
chat_agent = create_agent(
    chat_llm,
    chat_tools,
    system_prompt="""You are a friendly weather assistant. You can:
1. Look up weather information using the lookup_weather tool when users ask about weather
2. Have normal conversations about anything else

When presenting weather data, format it nicely in natural language. 
Remember previous conversations with the user.""",
    checkpointer=chat_checkpointer,
    # No response_format - allows natural conversation!
)


if __name__ == "__main__":
    print("Weather Chat Assistant (type 'exit' to quit)")
    print("-" * 45)

    while True:
        user_input = input("\nUser: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        result = chat_agent.invoke({
            "messages": [
                {"role": "user", "content": user_input}
            ]
        }, config={"configurable": {"thread_id": "user_session_1"}})
        
        print(f"\nAssistant: {result['messages'][-1].content}")