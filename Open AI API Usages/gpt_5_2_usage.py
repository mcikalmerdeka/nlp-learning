import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

response = client.responses.create(
    model="gpt-5.2",
    input="How much gold would it take to coat the Statue of Liberty in a 1mm layer?",
    reasoning={
        "effort": "none"
    },
    temperature=0.1,
    max_output_tokens=1000
)

response_text = response.output[0].content[0].text
print(response_text)