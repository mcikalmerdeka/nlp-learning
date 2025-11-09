import os
from pathlib import Path
from dotenv import load_dotenv

from textwrap import dedent

from agno.agent import Agent, RunOutput
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools
from agno.tools.file_generation import FileGenerationTools

# Load the environment variables and configure the OpenAI API key
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")    
EXA_API_KEY = os.getenv("EXA_API_KEY")

if not OPENAI_API_KEY or not EXA_API_KEY:
    raise ValueError("OPENAI_API_KEY and EXA_API_KEY must be set")

# Research Agent with Exa Tools
agent = Agent(
    model=OpenAIChat(id="gpt-4.1-mini", api_key=OPENAI_API_KEY),
    tools=[ExaTools(api_key=EXA_API_KEY)],
    instructions=dedent("""
        You are an expert research analyst with access to advanced research tools.
        
        When you are given a schema to use, pass it to the research tool as output_schema parameter to research tool. 

        The research tool has two parameters:
        - instructions (str): The research topic/question 
        - output_schema (dict, optional): A JSON schema for structured output

        Example: If user says "Research X. Use this schema {'type': 'object', ...}", you must call research tool with the schema.

        If no schema is provided, the tool will auto-infer an appropriate schema.

        Present the findings exactly as provided by the research tool.
    """),
)

# File Generation Agent with FileGenerationTools
file_generation_agent = Agent(
    model=OpenAIChat(id="gpt-4.1-mini", api_key=OPENAI_API_KEY),
    tools=[FileGenerationTools(output_directory="tmp/")],
    instructions=dedent("""
        You are an expert file generation analyst with access to advanced file generation tools.
    """),
    markdown=True
)
# Run the research agent
research_response: RunOutput = agent.run(
    """Perform a comprehensive research on the current flagship GPUs from NVIDIA, AMD and Intel. 
    Return a table of model name, MSRP USD, TDP watts, and launch date. Include citations for each cell."""
)

# Get the research output in the text format
research_output = str(research_response.content)

# Run the file generation agent
file_generation_response: RunOutput = file_generation_agent.run(
    dedent(f"""Generate a markdown report on the current flagship GPUs from NVIDIA, AMD and Intel based on the research agent's output.
    The research agent's output is: {research_output}
    Use the research agent's output as the context for the file generation."""))