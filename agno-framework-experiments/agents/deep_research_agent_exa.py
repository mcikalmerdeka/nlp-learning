import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

from textwrap import dedent
from agno.agent import Agent, RunOutput
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

# Load the environment variables and configure the OpenAI API key
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")    
EXA_API_KEY = os.getenv("EXA_API_KEY")

if not OPENAI_API_KEY or not EXA_API_KEY:
    raise ValueError("OPENAI_API_KEY and EXA_API_KEY must be set")

# # ============== Example 1: Flagship GPUs Research Agent =================

# # Research Agent with Exa Tools
# agent = Agent(
#     model=OpenAIChat(id="gpt-4.1-mini", api_key=OPENAI_API_KEY),
#     tools=[ExaTools(api_key=EXA_API_KEY)],
#     instructions=dedent("""
#         You are an expert research analyst with access to advanced research tools.
        
#         When you are given a schema to use, pass it to the research tool as output_schema parameter to research tool. 

#         The research tool has two parameters:
#         - instructions (str): The research topic/question 
#         - output_schema (dict, optional): A JSON schema for structured output

#         Example: If user says "Research X. Use this schema {'type': 'object', ...}", you must call research tool with the schema.

#         If no schema is provided, the tool will auto-infer an appropriate schema.

#         Present the findings exactly as provided by the research tool.
#     """),
# )

# # File Generation Agent with FileGenerationTools
# file_generation_agent = Agent(
#     model=OpenAIChat(id="gpt-4.1-mini", api_key=OPENAI_API_KEY),
#     tools=[FileGenerationTools(output_directory="tmp/")],
#     instructions=dedent("""
#         You are an expert file generation analyst with access to advanced file generation tools.
#     """),
#     markdown=True
# )
# # Run the research agent
# research_response: RunOutput = agent.run(
#     """Perform a comprehensive research on the current flagship GPUs from NVIDIA, AMD and Intel. 
#     Return a table of model name, MSRP USD, TDP watts, and launch date. Include citations for each cell."""
# )

# # Get the research output in the text format
# research_output = str(research_response.content)

# # Run the file generation agent
# file_generation_response: RunOutput = file_generation_agent.run(
#     dedent(f"""Generate a markdown report on the current flagship GPUs from NVIDIA, AMD and Intel based on the research agent's output.
#     The research agent's output is: {research_output}
#     Use the research agent's output as the context for the file generation."""))

# ============== Example 2: Academic Research Agent =================

# Initialize the academic research agent with scholarly capabilities
research_scholar = Agent(
    model=OpenAIChat(id="gpt-5-mini", api_key=OPENAI_API_KEY),
    tools=[

        # Use exa tools to search for academic research papers
        ExaTools(
            start_published_date=datetime.now().strftime("%Y-%m-%d"), type="keyword", api_key=EXA_API_KEY
        )
    ],
    description=dedent("""\
        You are a distinguished research scholar with expertise in multiple disciplines.
        Your academic credentials include: 📚

        - Advanced research methodology
        - Cross-disciplinary synthesis
        - Academic literature analysis
        - Scientific writing excellence
        - Peer review experience
        - Citation management
        - Data interpretation
        - Technical communication
        - Research ethics
        - Emerging trends analysis\
    """),
    instructions=dedent("""\
        1. Research Methodology 🔍
           - Conduct 3 distinct academic searches
           - Focus on peer-reviewed publications
           - Prioritize recent breakthrough findings
           - Identify key researchers and institutions

        2. Analysis Framework 📊
           - Synthesize findings across sources
           - Evaluate research methodologies
           - Identify consensus and controversies
           - Assess practical implications

        3. Report Structure 📝
           - Create an engaging academic title
           - Write a compelling abstract
           - Present methodology clearly
           - Discuss findings systematically
           - Draw evidence-based conclusions

        4. Quality Standards ✓
           - Ensure accurate citations
           - Maintain academic rigor
           - Present balanced perspectives
           - Highlight future research directions\
    """),
    expected_output=dedent("""\
        # {Engaging Title} 📚

        ## Abstract
        {Concise overview of the research and key findings}

        ## Introduction
        {Context and significance}
        {Research objectives}

        ## Methodology
        {Search strategy}
        {Selection criteria}

        ## Literature Review
        {Current state of research}
        {Key findings and breakthroughs}
        {Emerging trends}

        ## Analysis
        {Critical evaluation}
        {Cross-study comparisons}
        {Research gaps}

        ## Future Directions
        {Emerging research opportunities}
        {Potential applications}
        {Open questions}

        ## Conclusions
        {Summary of key findings}
        {Implications for the field}

        ## References
        {Properly formatted academic citations}

        ---
        Research conducted by AI Academic Scholar
        Published: {current_date}
        Last Updated: {current_time}\
    """),
    markdown=True,
    reasoning=True,
    add_datetime_to_context=True,
    save_response_to_file="tmp/{message}.md"
)

# Example usage with academic research request
if __name__ == "__main__":
    research_scholar.print_response(
        "Analyze recent developments in quantum computing architectures",
        stream=True,
    )

# Other topic examples to try:
# """
# Quantum Science & Computing:
# 1. "Investigate recent breakthroughs in quantum error correction"
# 2. "Analyze the development of topological quantum computing"
# 3. "Research quantum machine learning algorithms and applications"
# 4. "Explore advances in quantum sensing technologies"

# Biotechnology & Medicine:
# 1. "Examine recent developments in mRNA vaccine technology"
# 2. "Analyze breakthroughs in organoid research"
# 3. "Investigate advances in precision medicine"
# 4. "Research developments in neurotechnology"

# Materials Science:
# 1. "Explore recent advances in metamaterials"
# 2. "Analyze developments in 2D materials beyond graphene"
# 3. "Research progress in self-healing materials"
# 4. "Investigate new battery technologies"

# Artificial Intelligence:
# 1. "Examine recent advances in foundation models"
# 2. "Analyze developments in AI safety research"
# 3. "Research progress in neuromorphic computing"
# 4. "Investigate advances in explainable AI"
# """