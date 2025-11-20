from google import genai
from google.genai import types
from PIL import Image

import os
from dotenv import load_dotenv
load_dotenv()

# Initialize the client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Define the prompt
prompt = (
    "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"
)

# Generate the image
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[prompt],
)

# Save the image
for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("generated_image.png")