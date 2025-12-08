"""
This script demonstrates the basic usage of LangChain framework. Several features are showcased:
1. Tool calling
2. Structured output
3. Agent creation
"""

import os
from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field
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
    "Tokyo": 25,
    "New York": 15,
    "London": 10,
    "Sydney": 25,
    "Beijing": 10,
}

# Setup structured output
class WeatherReport(BaseModel):
    """Weather report for a specified city."""
    city: str = Field(..., description="The city of requested weather")
    weather: str = Field(..., description="The current weather on the specified city")
    temperature: int = Field(..., description="The current temperature on the specified city")

class WeatherReportList(BaseModel):
    """List of weather reports for multiple cities."""
    reports: list[WeatherReport] = Field(..., description="List of weather reports for each requested city")

# Initialize Tools
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a specified city."""

    # Simulate API call
    return weather_db.get(city, "unknown")

@tool
def get_temperature(city: str) -> int:
    """Get the current temperature for a specified city."""

    # Simulate API call
    return temperature_db.get(city, 0)

tools = [get_weather, get_temperature]

# Initialize Model and Agent
llm = ChatOpenAI(model="gpt-4o-mini",
                 openai_api_key=os.getenv("OPENAI_API_KEY"),
                 temperature=0.5,
                 max_tokens=200)

agent = create_agent(
    llm,                    # LLM with tool calling support
    tools,                  # List of tools
    response_format=WeatherReportList,
    system_prompt="You are a weather assistant with access to tools. Always return structured weather data for ALL cities requested by the user."
)

# Running option 1: Invoke the Agent
result = agent.invoke({
    "messages": [
        {"role": "user", 
        "content": "What's the weather and temperature in New York and Tokyo?"}
    ]
})

print(result["messages"][-1].content)

# # Running option 2: Streaming response
# for chunk in agent.stream({
#     "messages": [{"role": "user", "content": "What's the weather and temperature in New York and Tokyo?"}]
# }, stream_mode="values"):
#     if "messages" in chunk:
#         last_msg = chunk["messages"][-1]
#         if last_msg.content:
#             print(last_msg.content, end="", flush=True)