import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from pprint import pprint

# Define the model
model = ChatOpenAI(
    model="gpt-4.1-mini",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

# Create a function for the time conversion MCP
async def time_conversion_mcp():
    client = MultiServerMCPClient(
        {
            "time": {
                "transport": "stdio",
                "command": "uvx",
                "args": [
                    "mcp-server-time",
                    "--local-timezone=America/New_York"
                ]
            }
        }
    )
    tools = await client.get_tools()

    agent = create_agent(
        model=model, 
        tools=tools,
    )
    question = HumanMessage(content="What time is it?")
    response = await agent.ainvoke(
        {"messages": [question]}
    )
    pprint(response)

# Create a function for the travel agent MCP
async def travel_agent_mcp():
    client = MultiServerMCPClient(
        {
            "travel_server": {
                "transport": "streamable_http",
                "url": "https://mcp.kiwi.com"
            }
        }
    )

    tools = await client.get_tools()

    agent = create_agent(
    model=model,
    tools=tools,
    checkpointer=InMemorySaver(),
    system_prompt="You are a travel agent. No follow up questions."
)

    config = {"configurable": {"thread_id": "1"}}

    response = await agent.ainvoke(
        {"messages": [HumanMessage(content="Get me a direct flight from Jakarta to Palu on January 14th")]},
        config
    )

    pprint(response)

    print(response["messages"][-1].content)


if __name__ == "__main__":
    # asyncio.run(time_conversion_mcp())
    asyncio.run(travel_agent_mcp())
