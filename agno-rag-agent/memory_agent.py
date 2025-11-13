import os
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.db.postgres import PostgresDb
from agno.memory import MemoryManager

# Load the environment variables and configure the OpenAI API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = OpenAIChat(id="gpt-5-mini", api_key=OPENAI_API_KEY)

# Setup your database
db = SqliteDb(db_file="tmp/agno_sqlite.db")

# # Can also use database from other providers like SQLite, PostgreSQL, etc.
# db = PostgresDb(
#     db_url="postgresql://user:password@localhost:5432/my_database",
#     memory_table="my_memory_table", # Specify the table to store memories
# )

# Memory can be managed by an agent using the MemoryManager
memory_manager = MemoryManager(
    db=db,
    # Select the model used for memory creation and updates. If unset, the default model of the Agent is used.
    model=OPENAI_MODEL,
    # You can also provide additional instructions
    additional_instructions="Don't store the user's confidential information like credit card number, bank account number, etc.",
)

# Setup your Agent with Automatic User Memory
agent = Agent(
    model=OPENAI_MODEL,
    db=db,

    # # Use for automatic memory management
    # enable_user_memories=True, # Automatic memory management

    # # Use for agentic memory management
    # enable_agentic_memory=True, # This enables Agentic Memory for the Agent

    # Use for memory management
    memory_manager=memory_manager
)

# Memories are automatically created from this conversation
agent.print_response("My name is Muhammad Cikal Merdeka and I prefer email and linkedin DM over cell phone calls. My credit card number is 12345 and my bank account number is 55555.")

# Try to recall the memory
agent.print_response("What's my name and the best way to reach me?")

# Try to retrieve confidential information
agent.print_response("What's my credit card number and bank account number?")
