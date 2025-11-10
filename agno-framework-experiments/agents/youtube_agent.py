import os
from pathlib import Path
from dotenv import load_dotenv

from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.youtube import YouTubeTools

# Load the environment variables and configure the OpenAI API key
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")    

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY must be set")

youtube_agent = Agent(
    name="YouTube Agent",
    model=OpenAIChat(id="gpt-5-mini", api_key=OPENAI_API_KEY),
    tools=[YouTubeTools()],
        instructions=dedent("""\
        You are an expert YouTube content analyst with a keen eye for detail! 🎓
        Follow these steps for comprehensive video analysis:
        1. Video Overview
           - Check video length and basic metadata
           - Identify video type (tutorial, review, lecture, etc.)
           - Note the content structure
        2. Timestamp Creation
           - Create precise, meaningful timestamps
           - Focus on major topic transitions
           - Highlight key moments and demonstrations
           - Format: [start_time, end_time, detailed_summary]
        3. Content Organization
           - Group related segments
           - Identify main themes
           - Track topic progression

        Your analysis style:
        - Begin with a video overview
        - Use clear, descriptive segment titles
        - Include relevant emojis for content types:
          📚 Educational
          💻 Technical
          🎮 Gaming
          📱 Tech Review
          🎨 Creative
        - Highlight key learning points
        - Note practical demonstrations
        - Mark important references

        Quality Guidelines:
        - Verify timestamp accuracy
        - Avoid timestamp hallucination
        - Ensure comprehensive coverage
        - Maintain consistent detail level
        - Focus on valuable content markers
    """),
    add_datetime_to_context=True,
    markdown=True,
)

# Example usage with different types of videos
video_url = "https://youtu.be/4KxNJX0c2ZU?si=CTAg3lYAcXCE0q5r" 
youtube_agent.print_response(
    f"Analyze this video: {video_url}",
    stream=True
)

# # More example prompts to explore:
# """
# Tutorial Analysis:
# 1. "Break down this Python tutorial with focus on code examples"
# 2. "Create a learning path from this web development course"
# 3. "Extract all practical exercises from this programming guide"
# 4. "Identify key concepts and implementation examples"

# Educational Content:
# 1. "Create a study guide with timestamps for this math lecture"
# 2. "Extract main theories and examples from this science video"
# 3. "Break down this historical documentary into key events"
# 4. "Summarize the main arguments in this academic presentation"

# Tech Reviews:
# 1. "List all product features mentioned with timestamps"
# 2. "Compare pros and cons discussed in this review"
# 3. "Extract technical specifications and benchmarks"
# 4. "Identify key comparison points and conclusions"

# Creative Content:
# 1. "Break down the techniques shown in this art tutorial"
# 2. "Create a timeline of project steps in this DIY video"
# 3. "List all tools and materials mentioned with timestamps"
# 4. "Extract tips and tricks with their demonstrations"
# """

# Output:
# (.venv) PS E:\NLP Learning\NLP-Learning\agno-framework-experiments> uv run .\agents\youtube_agent.py
# ┏━ Message ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                                                                                                   ┃
# ┃ Analyze this video: https://youtu.be/4KxNJX0c2ZU?si=CTAg3lYAcXCE0q5r                                                                                              ┃
# ┃                                                                                                                                                                   ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
# ┏━ Response (36.6s) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
# ┃                                                                                                                                                                   ┃
# ┃ Video overview                                                                                                                                                    ┃
# ┃                                                                                                                                                                   ┃
# ┃  • Title: AGI progress can’t be quantified – Andrej Karpathy                                                                                                      ┃
# ┃  • Channel / author: Dwarkesh Clips                                                                                                                               ┃
# ┃  • Speaker: Andrej Karpathy (clip of an interview)                                                                                                                ┃
# ┃  • Video length: ~9:27                                                                                                                                            ┃
# ┃  • Video type: 📚 Educational / 💻 Technical interview clip — focused discussion on how to measure AGI progress and where automation is showing up first.         ┃
# ┃  • Structure: short interview excerpt with a single, continuous discussion that moves from definitions of AGI → which jobs are automatable → the concept of       ┃
# ┃    partial automation/autonomy sliders → why coding is currently the primary beneficiary of LLMs/agents.                                                          ┃
# ┃                                                                                                                                                                   ┃
# ┃ Timestamped segments Format: [start_time, end_time, detailed_summary]                                                                                             ┃
# ┃                                                                                                                                                                   ┃
# ┃  • [00:00, 00:32] — Opening question: ways people try to “chart” AGI progress                                                                                     ┃
# ┃     • Host frames common proposals (education-level analogies, task-horizon analogies).                                                                           ┃
# ┃     • Speaker reacts skeptically to simple y-axis proposals.                                                                                                      ┃
# ┃  • [00:32, 01:26] — Definition of AGI and scope concession 📚                                                                                                     ┃
# ┃     • Speaker restates a working definition: a system that can do any economically valuable task at human-level or better.                                        ┃
# ┃     • Notes the common concession to restrict AGI to digital knowledge work (excludes physical tasks) and raises the question of what fraction of the economy     ┃
# ┃       that covers.                                                                                                                                                ┃
# ┃  • [01:26, 03:08] — Measuring impact: tasks vs jobs; radiology example 🎯                                                                                         ┃
# ┃     • Distinguishes tasks from jobs and highlights societal refactoring when tasks are automated.                                                                 ┃
# ┃     • Examines Jeff Hinton’s radiologist prediction and explains why radiology has proven messy and resistant to simple replacement despite strong                ┃
# ┃       computer-vision capabilities.                                                                                                                               ┃
# ┃  • [03:08, 04:32] — Call centers as a candidate for early automation 💻                                                                                           ┃
# ┃     • Argues call center work is highly automatable: repetitive tasks, constrained context, purely digital.                                                       ┃
# ┃     • Introduces the idea of a gradual “autonomy slider” (AIs handle bulk of volume; humans handle edge cases and supervise multiple AIs).                        ┃
# ┃  • [04:32, 06:00] — The “last 1%” bottleneck and wage dynamics ⚖️                                                                                                  
# ┃
# ┃     • Analogy: early autonomous systems still having a human in the loop (e.g., deployed robo-taxis).                                                             ┃
# ┃     • If humans remain required for the last critical fraction, those roles become highly valuable/non-fungible, possibly driving wages up until full automation  ┃
# ┃       removes the bottleneck.                                                                                                                                     ┃
# ┃  • [06:00, 07:08] — Observed deployment pattern: coding first, not uniform gains across knowledge work 🔍                                                         ┃
# ┃     • Notes that rather than a uniform erosion across professions, current LLM/agent deployment seems to favor programmers and coding use-cases.                  ┃
# ┃     • API revenue and real-world adoption skew heavily toward coding assistance.                                                                                  ┃
# ┃  • [07:08, 09:15] — Why coding is the “perfect first” use-case for LLMs 💻📚                                                                                      ┃
# ┃     • Coding is fundamentally text-based and aligns with how LLMs are trained.                                                                                    ┃
# ┃     • There’s pre-existing infrastructure (IDEs, diffs, version control) that makes agent outputs easy to inspect, review, and integrate.                         ┃
# ┃     • Contrasts with harder domains (slides, spatial graphics) where no ready “diff”/infrastructure exists, making automation and human review harder.            ┃
# ┃  • [09:15, 09:27] — Close / call-to-action                                                                                                                        ┃
# ┃     • Clip end and channel subscribe prompt.                                                                                                                      ┃
# ┃                                                                                                                                                                   ┃
# ┃ Content organization and progression                                                                                                                              ┃
# ┃                                                                                                                                                                   ┃
# ┃  • Main themes                                                                                                                                                    ┃
# ┃     1 Definition and measurability of AGI (what to measure)                                                                                                       ┃
# ┃     2 Practical lens: tasks vs. jobs and economic impact                                                                                                          ┃
# ┃     3 Gradual automation model (autonomy slider and human-in-the-loop)                                                                                            ┃
# ┃     4 Real-world deployment pattern favoring coding because of data/infrastructure fit                                                                            ┃
# ┃  • How topics progress                                                                                                                                            ┃
# ┃     • Starts at the abstract question of metrics → narrows to definition and scope → moves to empirical examples (radiology, call centers) → introduces           ┃
# ┃       economic/organizational consequences (bottlenecks, wages) → concludes with a technical explanation for observed deployment (text+infrastructure bias toward ┃
# ┃       code).                                                                                                                                                      ┃
# ┃                                                                                                                                                                   ┃
# ┃ Key learning points                                                                                                                                               ┃
# ┃                                                                                                                                                                   ┃
# ┃  • “AGI progress” is hard to compress to a single numeric y-axis — practical definitions matter (economically valuable tasks at human level).                     ┃
# ┃  • Restricting AGI to digital knowledge work is a major concession; it still covers a huge economic slice, but not the entire economy.                            ┃
# ┃  • Tasks (not whole jobs) are the right unit for thinking about automation, but jobs will be refactored around what remains automatable.                          ┃
# ┃  • Expect gradual, partial automation: AIs will likely handle most routine volume while humans supervise and handle edge cases (autonomy slider).                 ┃
# ┃  • The last small fraction of a job can become the bottleneck and the most valuable human role until it’s removed.                                                ┃
# ┃  • Current LLM/agent impact is non-uniform: coding tools have seen outsized adoption because they match LLM strengths (text-based) and benefit from existing      ┃
# ┃    developer tooling (diffs, IDEs, VCS).                                                                                                                          ┃
# ┃  • Domains without that textual/infrastructure fit (e.g., spatial slide design) are harder to automate and require additional tooling to reach parity.            ┃
# ┃                                                                                                                                                                   ┃
# ┃ Practical demonstrations / examples highlighted                                                                                                                   ┃
# ┃                                                                                                                                                                   ┃
# ┃  • Radiology (as a counterexample of easy automation)                                                                                                             ┃
# ┃  • Call center workflows (example of high automability)                                                                                                           ┃
# ┃  • Robo-taxi human-in-the-loop analogy                                                                                                                            ┃
# ┃  • Coding workflows, diffs, and IDE integration as practical enablers for LLM agents                                                                              ┃
# ┃                                                                                                                                                                   ┃
# ┃ Important references mentioned                                                                                                                                    ┃
# ┃                                                                                                                                                                   ┃
# ┃  • Jeff Hinton’s prediction about radiologists                                                                                                                    ┃
# ┃  • Robo-taxi deployments (human oversight analogy)                                                                                                                ┃
# ┃  • Developer tooling: Visual Studio Code / diffs / version control as enabling infrastructure                                                                     ┃
# ┃                                                                                                                                                                   ┃
# ┃ Use recommendations (for creators / editors)                                                                                                                      ┃
# ┃                                                                                                                                                                   ┃
# ┃  • If adding chapter markers, use the timestamps above as chapter starts.                                                                                         ┃
# ┃  • For an excerpted clip title/description: emphasize “Why coding benefits first from LLMs” and “autonomy slider” to attract technical and policy-interested      ┃
# ┃    viewers.                                                                                                                                                       ┃
# ┃  • Tags/SEO suggestions: AGI definition, Andrej Karpathy, automation, LLMs in coding, call center automation, human-in-the-loop.                                  ┃
# ┃                                                                                                                                                                   ┃
# ┃ If you want, I can:                                                                                                                                               ┃
# ┃                                                                                                                                                                   ┃
# ┃  • Convert the above into YouTube chapter markup you can paste into the video description.                                                                        ┃
# ┃  • Produce short captioned social clips for the most salient 30–60s moments (e.g., the coding vs slides point or the autonomy-slider analogy).                    ┃
# ┃                                                                                                                                                                   ┃
# ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛