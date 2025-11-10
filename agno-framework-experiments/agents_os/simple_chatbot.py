import os
from pathlib import Path
from dotenv import load_dotenv

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.tools.mcp import MCPTools

# Load the environment variables and configure the OpenAI API key
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")    

# Setup database (SQLite for quick prototyping)
db = SqliteDb(db_file=str(BASE_DIR / "agentos.db"))

# Create MCPTools instance (connects to Agno documentation MCP server)
# AgentOS automatically manages MCP lifecycle - no need to manually connect/disconnect
mcp_tools = MCPTools(
    transport="streamable-http", 
    url="https://docs.agno.com/mcp"
)

# Create a chatbot agent with conversation memory and MCP tools
agent = Agent(
    name="Chatbot Assistant",
    id="chatbot-assistant",
    model=OpenAIChat(id="gpt-4o-mini", api_key=OPENAI_API_KEY),
    db=db,
    tools=[mcp_tools],
    instructions=["You are a helpful AI assistant chatbot. Be friendly, conversational, and helpful."],
    enable_user_memories=True,
    add_history_to_context=True,  # Enables conversation continuity
    num_history_runs=3,  # Includes last 3 conversation turns for context
    markdown=True,
)

# Create AgentOS app
agent_os = AgentOS(
    description="Simple chatbot with MCP tools and conversation memory",
    agents=[agent],
)   

app = agent_os.get_app()

if __name__ == "__main__":
    # Start the server
    # Note: Don't use reload=True with MCP tools to avoid connection issues
    agent_os.serve(app="agent_os_quickstart:app", reload=False)
    # Visit http://localhost:7777 to interact with your chatbot