# ## Invoking a Chat Prompt Template
# """
# The most common way to handle modern LLMs is with message-based chat prompts. 
# 1. Define the template: Import ChatPromptTemplate and define your messages.
# 2. Invoke the template: Call .invoke() with a dictionary containing the values for your placeholders. 
# """

# from langchain_core.prompts import ChatPromptTemplate

# # 1. Define the template with placeholders like {user_input}
# template = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are a helpful AI bot named {name}."),
#         ("human", "{user_input}"),
#     ]
# )

# # 2. Invoke the template with the required input variables
# prompt_value = template.invoke({"name": "Carl", "user_input": "Hello, how are you?"})

# # The result is a ChatPromptValue object which contains formatted messages
# print(prompt_value.messages)


## Invoking a String Prompt Template
"""
For models that only accept a single string as input, you can use PromptTemplate and .invoke(). 
"""

from langchain_core.prompts import PromptTemplate

# 1. Define the template string
prompt_str = "Tell me a joke about {topic}."

# 2. Create the PromptTemplate instance
prompt = PromptTemplate.from_template(prompt_str)

# 3. Invoke the template
prompt_value = prompt.invoke({"topic": "chickens"})

# The result is a PromptValue object, its string value can be accessed via .to_string()
print(prompt_value.to_string())


## Using the Prompt with a Model
"""
Once you have the PromptValue (the formatted prompt), you can pass it to an LLM or a chain for generating a response. 
"""

import os
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI

# Initialize the model
model = ChatOpenAI(model="gpt-4.1-nano", api_key=os.getenv("OPENAI_API_KEY"))

# Invoke the model with the prompt
response = model.invoke(prompt_value)

# The result is a string
print(response.content)