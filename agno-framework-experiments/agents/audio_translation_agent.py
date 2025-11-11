import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from textwrap import dedent

from agno.agent import Agent, RunOutput
from agno.models.anthropic import Claude
from agno.tools.cartesia import CartesiaTools
from agno.utils.media import save_base64_data

# Load the environment variables and configure the OpenAI API key
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not CARTESIA_API_KEY or not ANTHROPIC_API_KEY:
    raise ValueError("CARTESIA_API_KEY and ANTHROPIC_API_KEY must be set")

# Define the agent instructions
agent_instructions = dedent(
    """Follow these steps SEQUENTIALLY to translate text and generate a voice note:
    1. Identify the text to translate and the target language from the user request.
    2. Translate the text accurately to the target language. Keep this translated text for the final audio generation step.
    3. Analyze the emotion conveyed by the *translated* text (e.g., neutral, happy, sad, angry, etc.).
    4. Call the 'list_voices' tool to get a list of available Cartesia voices. Wait for the result.
    5. Examine the list of voices from the 'list_voices' result. Select the 'id' of an *existing* voice that:
       a) Matches the target language (e.g., 'en' for English).
       b) Best reflects the analyzed emotion (from step 3).
    6. Call the 'text_to_speech' tool to generate the audio. Provide:
        - 'transcript': The translated text from step 2.
        - 'voice_id': The voice_id selected in step 5.
    """
)

# Create the agent
agent = Agent(
    name="Emotion-Aware Translator Agent",
    description="Translates text, analyzes emotion, selects a suitable voice, and generates a voice note (audio file) using Cartesia TTS tools.",
    instructions=agent_instructions,
    model=Claude(id="claude-sonnet-4-5-20250929", api_key=ANTHROPIC_API_KEY),
    tools=[CartesiaTools(api_key=CARTESIA_API_KEY)],
)

text_to_translate = "Halo! Apa kabar? Ceritakan lebih banyak tentang cuaca di Indonesia?"
response: RunOutput = agent.run(
    f"Convert this Indonesian phrase '{text_to_translate}' to English and create a voice note"
)

print("\nChecking for Audio Artifacts on Agent...")
if response.audio:
    base64_audio = base64.b64encode(response.audio[0].content).decode("utf-8")
    save_base64_data(base64_audio, "tmp/english_greeting.mp3")
    print(f"Audio saved to tmp/english_greeting.mp3")