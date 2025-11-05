import os
from dotenv import load_dotenv
from typing import Iterator

from agno.agent import Agent, RunOutput, RunOutputEvent, RunEvent
from agno.models.openai import OpenAIChat
from agno.tools.tavily import TavilyTools
from agno.utils.pprint import pprint_run_response

# Load the environment variables and configure the OpenAI API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

# Initialize the Agent with instructions, tools, and a model
agent = Agent(
    name="Research Assistant",
    model=OpenAIChat(id="gpt-4.1-mini", api_key=openai_api_key),
    description="""
    You are a Research Assistant specialized in finding and analyzing information about technology trends, 
    startups, and emerging markets. You provide comprehensive research reports with actionable insights.
    """,
    instructions="Write a report on the topic. Output only the report.",
    tools=[TavilyTools(api_key=tavily_api_key)],
    markdown=True
)

# Define the query
query = "Trending startups that focuses on the AI Agentic technology"

# Run the Agent (.print_response() is for development purposes)
# agent.print_response(query, stream=True)

# # Run the Agent (.run() is for production purposes)
# response: RunOutput = agent.run(query)
# print(response.content)

################ STREAM RESPONSE #################
stream: Iterator[RunOutputEvent] = agent.run(query, stream=True)
for chunk in stream:
    if chunk.event == RunEvent.run_content:
        print(chunk.content)

# # ################ STREAM AND PRETTY PRINT #################
# stream: Iterator[RunOutputEvent] = agent.run(query, stream=True)
# pprint_run_response(stream, markdown=True)

# Output:

# (.venv) PS E:\NLP Learning\NLP-Learning\Agno AI Agent Experiment> uv run agno_implementation.py
# ╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
# │ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
# │ ┃                                                       Report on Trending Startups Focusing on AI Agentic Technology                                                       ┃ │
# │ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │
# │                                                                                                                                                                               │
# │                                                                                                                                                                               │
# │                                                                                 Introduction                                                                                  │
# │                                                                                                                                                                               │
# │ AI Agentic technology refers to autonomous AI systems capable of independently planning, acting, and delivering measurable outcomes across various industries. Unlike simple  │
# │ AI frameworks or APIs, agentic AI startups focus on building fully autonomous systems that optimize workflows without continuous human intervention. This report highlights   │
# │ notable trending startups innovating within the AI agentic space, discussing their domain focuses, innovations, and growth potential.                                         │
# │                                                                                                                                                                               │
# │ ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
# │                                                                                                                                                                               │
# │                                                                   Notable Startups in AI Agentic Technology                                                                   │
# │                                                                                                                                                                               │
# │                                                                                  1. Octonomy                                                                                  │
# │                                                                                                                                                                               │
# │  • Focus: Complex enterprise workflow automation in technical environments                                                                                                    │
# │  • Highlights: Raised $20 million to scale agentic AI that addresses complex, multi-source technical data and automates end-to-end workflows.                                 │
# │  • Differentiator: More advanced integration and agentic capabilities than conversational AI-based competitors like Ada Support or Ultimate.ai.                               │
# │  • Potential: Key player in enterprise automation with AI capable of handling sophisticated and varied technical processes.                                                   │
# │                                                                                                                                                                               │
# │                                                                                   2. Decidr                                                                                   │
# │                                                                                                                                                                               │
# │  • Focus: Agentic AI for Human Resources and talent management                                                                                                                │
# │  • Founded: 2020                                                                                                                                                              │
# │  • Highlights: Uses agentic AI systems for enhancing hiring, internal mobility, and learning within large organizations.                                                      │
# │  • Innovation: Rethinks talent management by bringing autonomous decision-making capabilities to HR functions.                                                                │
# │                                                                                                                                                                               │
# │                                                                               3. Hippocratic AI                                                                               │
# │                                                                                                                                                                               │
# │  • Focus: Safety-first healthcare AI agents                                                                                                                                   │
# │  • Funding: Raised $141 million in Series B funding                                                                                                                           │
# │  • Highlights: Creates voice-based healthcare agents following medical protocols for patient communication, appointment management, and discharge follow-ups.                 │
# │  • Significance: Combines empathy with regulatory compliance to safely scale human care via AI automation.                                                                    │
# │                                                                                                                                                                               │
# │                                                                                   4. Aegis                                                                                    │
# │                                                                                                                                                                               │
# │  • Focus: Autonomous insurance claim appeal agent                                                                                                                             │
# │  • Founded: 2021                                                                                                                                                              │
# │  • Highlights: Streamlines insurance claim processing by automating complex appeals and claim resolution workflows.                                                           │
# │  • Impact: Reduces manual paperwork and long wait times in insurance, improving customer experience and operational efficiency.                                               │
# │                                                                                                                                                                               │
# │                                                                                  5. Descope                                                                                   │
# │                                                                                                                                                                               │
# │  • Focus: Agentic identity and policy-based governance                                                                                                                        │
# │  • Highlights: Provides an Agentic Identity Control Plane supporting identity management and auditing of AI agents.                                                           │
# │  • Funding: Recently closed a $35 million seed round.                                                                                                                         │
# │  • Importance: Enables secure and compliant deployment of AI agents with governance controls, vital for enterprise adoption.                                                  │
# │                                                                                                                                                                               │
# │                                                                                  6. Straiker                                                                                  │
# │                                                                                                                                                                               │
# │  • Focus: Agentic security with attack and defense AI agents                                                                                                                  │
# │  • Highlights: Offers continuous security testing and automated enforcement through AI trained on real-world agentic threats.                                                 │
# │  • Innovation: Provides the first comprehensive agentic AI security solution addressing emerging AI-specific risks.                                                           │
# │                                                                                                                                                                               │
# │                                                                               7. Noma Security                                                                                │
# │                                                                                                                                                                               │
# │  • Focus: AI and agentic risk management                                                                                                                                      │
# │  • Highlights: Delivers a platform for continuous discovery, inventory, risk prioritization, and security posture management of AI applications and agents.                   │
# │  • Value: Supports organizations in controlling security and compliance risk associated with deploying multiple AI agents.                                                    │
# │                                                                                                                                                                               │
# │ ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
# │                                                                                                                                                                               │
# │                                                                    Emerging Trends in AI Agentic Startups                                                                     │
# │                                                                                                                                                                               │
# │  • Domain-Specific Agents: Startups are building agentic AI systems tailored to specific industries like healthcare (Hippocratic AI), insurance (Aegis), HR (Decidr), and     │
# │    enterprise automation (Octonomy).                                                                                                                                          │
# │  • Autonomy with Compliance: Emphasis on safe, compliant AI operation incorporating regulatory standards, especially in sensitive sectors such as healthcare.                 │
# │  • Security and Governance: Growing focus on identity management, policy enforcement, and AI-agent risk control to build trust and scalability.                               │
# │  • Workflow Optimization: Agentic AI is shifting businesses from reactive to self-optimizing operations by autonomously managing complex, multi-step processes.               │
# │  • Funding Momentum: Significant venture funding rounds indicate strong investor confidence in agentic AI's commercial viability.                                             │
# │                                                                                                                                                                               │
# │ ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
# │                                                                                                                                                                               │
# │                                                                                  Conclusion                                                                                   │
# │                                                                                                                                                                               │
# │ AI Agentic technology is gaining strong traction with startups pushing the boundaries of fully autonomous AI systems. By focusing on domain-specific autonomy, compliance,    │
# │ security, and workflow optimization, these startups are transforming industries with AI agents that can act independently and responsibly. The investment momentum and        │
# │ expanding capabilities of these startups signal that agentic AI will be a cornerstone of next-generation automation and AI-driven enterprise transformation.                  │
# │                                                                                                                                                                               │
# │ ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
# │                                                                                                                                                                               │
# │                                                                             Key Startups to Watch                                                                             │
# │                                                                                                                                                                               │
# │                                                                                                                                                                               │
# │   Startup          Domain                 Notable Feature                        Latest Funding                                                                               │
# │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                                                              │
# │   Octonomy         Enterprise Workflow    Complex multi-source data handling     $20M Seed                                                                                    │
# │   Decidr           Human Resources        AI-driven talent management            -                                                                                            │
# │   Hippocratic AI   Healthcare             Voice-based compliant care agents      $141M Series B                                                                               │
# │   Aegis            Insurance              Autonomous claim appeals               -                                                                                            │
# │   Descope          AI Identity Security   Agentic Identity Control Plane         $35M Seed                                                                                    │
# │   Straiker         AI Security            Attack/Defense AI agents               -                                                                                            │
# │   Noma Security    AI Risk Management     Continuous AI agent discovery & risk   -                                                                                            │
# │                                                                                                                                                                               │
# │                                                                                                                                                                               │
# │ ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
# │ This emerging landscape demonstrates that AI agentic technology startups are poised to revolutionize autonomous system deployment across diverse markets. Keeping an eye on   │
# │ these innovators offers valuable insights into the future of AI-driven business automation and operational excellence.                                                        │
# ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯