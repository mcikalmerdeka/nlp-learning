# 🔗 Introduction to LangChain - Python

## Introduction

Welcome to LangChain Academy's Introduction to LangChain course!

---

## 🚀 Setup

### Prerequisites

- The Chrome browser is recommended
- Ensure you're using Python >=3.12, <3.14 [More info](#virtual-environments-and-python)
- A package manager: [uv](https://docs.astral.sh/uv/) (recommended) or [pip](https://pypi.org/project/pip/)
- [Node.js](http://nodejs.org/) and npx (only required for MCP server in module-2):


### Installation

Download the course repository
```bash
# Clone the repo
git clone https://github.com/langchain-ai/lca-lc-foundations.git
cd lca-lc-foundations
```

Make a copy of example.env
```bash
# Create .env file
cp example.env .env
```

Edit the .env file to include the keys below. [More info](#model-providers)
```bash
# Required for model usage
OPENAI_API_KEY='your_openai_api_key_here'
TAVILY_API_KEY='your_tavily_api_key_here'

# optional, only used in Lesson 1 once
ANTHROPIC_API_KEY='your_anthropic_api_key_here'
GOOGLE_API_KEY='your_google_api_key_here'

# Optional for evaluation and tracing
LANGSMITH_API_KEY='your_langsmith_api_key_here'
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=lca-lc-foundation
# Uncomment the following if you are on the EU instance:
#LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
```

Make a virtual environment and install dependencies

<details open>
<summary>Using uv (recommended)</summary>

```bash
uv sync
```

</details>

<details>
<summary>Using pip</summary>

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

</details>

### Quick Start Verification

After completing the Setup section, you can run this command to verify your environment:

<details open>
<summary>Using uv</summary>

```bash
uv run python3 env_utils.py
```

</details>

<details>
<summary>Using pip</summary>

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python3 env_utils.py
```

</details>

## 💡 Development Environment

### Run Notebooks using either Jupyter or Cursor [More Info](#development-environment)

<details open>
<summary>Using uv</summary>

```bash
uv run jupyter lab
```

</details>

<details>
<summary>Using pip</summary>

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
jupyter lab
```

</details>


## 📚 Lessons
This repository contains three Modules that serve as introductions to many of LangChain's most-used features.

---

### Module 1: Create Agent

- Foundational models
- Tools
- Short-Term Memory
- Multimodal Messages
- Project: Personal Chef

### Module 2: Advanced Agent

- Model Context Protocol (MCP)
- Context and State
- Multi-Agent Systems
- Project: Wedding Planner

### Module 3: Production-Ready Agent

- What is Middleware?
- Managing Long Conversations
- Human In The Loop (HITL)
- Dynamic Agents
- Project: Email Assistant
- Bonus: Agent Chat UI

## 📖 Related Resources

### Virtual Environments and Python

Managing your Python version is often best done with virtual environments. This allows you to select a Python version for the course independent of the system Python version.

<details open>
<summary>Using uv (recommended)</summary>

You can select and install the Python version when creating the virtual environment with uv. For additional information, please see [uv](https://docs.astral.sh/uv/).

```bash
uv venv --python 3.12
source .venv/bin/activate
uv sync
```

</details>

<details>
<summary>Using pyenv + pip</summary>

If you are using pip instead of uv, you may prefer using pyenv to manage your Python versions. For additional information, please see [pyenv](https://github.com/pyenv/pyenv).

```bash
pyenv install 3.12
pyenv local 3.12
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

</details>

### Model Providers

If you don't have an OpenAI API key, you can sign up [here](https://openai.com/index/openai-api/). The course primarily uses gpt-5-nano which is very inexpensive.
You may also obtain additional API keys for [Anthropic](https://console.anthropic.com) or [Google](https://docs.langchain.com/oss/python/integrations/providers/google). These models are only used in the first lesson.

This course has been created using particular models and model providers.  You can use other providers, but you will need to update the API keys in the .env file and make some necessary code changes. LangChain supports many chat model providers [here](https://docs.langchain.com/oss/python/integrations/providers/all_providers).

Tavily is a search provider that returns search results in an LLM-friendly way. They have a generous free tier. [Tavily](https://tavily.com)

### Getting Started with LangSmith

- Create a [LangSmith](https://smith.langchain.com/) account
- Create a LangSmith API key

<img width="600" alt="LangSmith Dashboard" src="https://github.com/user-attachments/assets/e39b8364-c3e3-4c75-a287-d9d4685caad5" />

<img width="600" alt="LangSmith API Keys" src="https://github.com/user-attachments/assets/2e916b2d-e3b0-4c59-a178-c5818604b8fe" />

- Update your .env file you created with your new LangSmith API Key.

For more information on LangSmith, see our docs [here](https://docs.langchain.com/langsmith/home).

### Environment Variables

This course uses the [dotenv](https://pypi.org/project/python-dotenv) module to read key-value pairs from the .env file and set them in the environment in the Jupyter notebook. They do not need to be set globally in the terminal.

### Development Environment

Two popular IDEs that can use notebook files are [Jupyter](https://Jupyter.org/install) and [Cursor](https://cursor.com/download).  Jupyter can be installed locally in the virtual environment with pip if desired.
