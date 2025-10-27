# Langfuse Observability Setup Guide

## Overview

Langfuse is an open-source LLM engineering platform that provides comprehensive tracing capabilities for understanding and debugging LLM applications. It's framework agnostic and supports all major LLM providers including OpenAI, Anthropic, and more.

## Why Langfuse?

### Key Benefits

Langfuse captures complete traces of your LLM applications using OpenTelemetry, with support for all popular LLM/agent libraries. This makes it ideal for:

- **Cost Management**: Track token usage and costs across all providers
- **Quality Monitoring**: Debug prompts, responses, and workflow issues
- **Performance Optimization**: Identify latency bottlenecks
- **Multi-Provider Support**: Works with any LLM provider (OpenAI, Anthropic, Azure, etc.)

## Installation

### Required Packages

```bash
# Core Langfuse SDK (v3 - OpenTelemetry-based)
pip install langfuse

# Provider SDKs
pip install openai
pip install anthropic

# Optional: LiteLLM for unified multi-provider access
pip install litellm

# Optional: OpenTelemetry instrumentation for Anthropic
pip install opentelemetry-instrumentation-anthropic
```

## Setup Instructions

### 1. Get Langfuse API Keys

1. **Sign up**: Visit [https://cloud.langfuse.com](https://cloud.langfuse.com) (free tier available)
2. **Create a project**: Navigate to your project settings
3. **Get API keys**: Copy your Public Key and Secret Key

### 2. Configure Environment Variables

```bash
# Langfuse Configuration
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_HOST="https://cloud.langfuse.com"  # EU region
# export LANGFUSE_HOST="https://us.cloud.langfuse.com"  # US region

# LLM Provider Keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Verify Connection

```python
from langfuse import get_client

langfuse = get_client()

if langfuse.auth_check():
    print("✓ Connected to Langfuse!")
else:
    print("✗ Authentication failed")
```

## Integration Methods

### Method 1: @observe Decorator (Easiest)

The @observe() decorator makes it easy to trace any Python LLM application.

```python
from langfuse import observe
from langfuse.openai import openai

@observe()
def generate_story():
    return openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Tell me a story"}]
    ).choices[0].message.content

generate_story()
```

### Method 2: OpenTelemetry Instrumentation (Anthropic)

Use third-party OpenTelemetry-based instrumentation libraries to automatically trace API calls.

```python
from anthropic import Anthropic
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
from langfuse import get_client

# Auto-instrument all Anthropic calls
AnthropicInstrumentor().instrument()

langfuse = get_client()
client = Anthropic()

with langfuse.start_as_current_span(name="my-workflow"):
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello"}]
    )
```

### Method 3: Context Managers (More Control)

Context managers automatically handle the start and end of spans and set the current span in context for automatic nesting of child spans.

```python
from langfuse import get_client

langfuse = get_client()

with langfuse.start_as_current_span(name="process-request") as span:
    # Your processing logic
    span.update(output="Processing complete")
    
    with langfuse.start_as_current_generation(
        name="llm-call",
        model="gpt-4o"
    ) as generation:
        # LLM call
        generation.update(output="Generated response")

langfuse.flush()  # Important for short-lived apps
```

### Method 4: LiteLLM Integration

LiteLLM allows you to use any of 100+ models without changing your code, with full observability.

```python
import litellm

# Configure callbacks
litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]

# Use any provider
response = litellm.completion(
    model="gpt-4o",  # or "claude-sonnet-4-20250514"
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Provider-Specific Examples

### OpenAI

```python
from langfuse.openai import openai

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Anthropic Claude

**Option A: OpenTelemetry (Recommended)**
```python
from anthropic import Anthropic
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

AnthropicInstrumentor().instrument()
client = Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Option B: OpenAI-Compatible Endpoint**
```python
from langfuse.openai import OpenAI

client = OpenAI(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    base_url="https://api.anthropic.com/v1/"
)

response = client.chat.completions.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Azure OpenAI

```python
from langfuse.openai import AzureOpenAI

client = AzureOpenAI(
    api_key="...",
    api_version="2024-02-01",
    azure_endpoint="https://..."
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Advanced Features

### Nested Traces (RAG Example)

```python
@observe()
def retrieve_documents(query: str):
    # Vector DB retrieval
    return ["doc1", "doc2"]

@observe()
def generate_answer(query: str, docs: list):
    # LLM generation
    return "Answer based on docs"

@observe()
def rag_pipeline(query: str):
    docs = retrieve_documents(query)
    answer = generate_answer(query, docs)
    return answer
```

### Custom Metadata and Scoring

```python
with langfuse.start_as_current_span(
    name="user-query",
    metadata={
        "user_id": "user123",
        "environment": "production"
    }
) as span:
    # Process request
    
    # Score the trace
    span.score_trace(
        name="user-feedback",
        value=1,
        comment="Great response!"
    )
```

### Usage and Cost Tracking

Langfuse automatically calculates cost for ingested generations if usage is provided and a matching model definition exists.

```python
with langfuse.start_as_current_generation(
    name="anthropic-call",
    model="claude-3-opus-20240229"
) as generation:
    response = anthropic_client.messages.create(...)
    
    generation.update(
        output=response.content[0].text,
        usage_details={
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
        },
        # Optional: provide exact costs
        cost_details={
            "input": 0.015,  # USD
            "output": 0.075
        }
    )
```

## Best Practices

### 1. Always Flush in Short-Lived Apps

```python
# Before app/function exits
langfuse.flush()
```

### 2. Use Meaningful Trace Names

```python
@observe(name="summarize-customer-feedback")
def summarize(text):
    pass
```

### 3. Add Relevant Metadata

```python
@observe(metadata={"user_id": "123", "feature": "chat"})
def process():
    pass
```

### 4. Handle Errors Gracefully

```python
try:
    result = openai.chat.completions.create(...)
except Exception as e:
    langfuse.update_current_observation(
        level="ERROR",
        status_message=str(e)
    )
    raise
```

## Viewing Your Traces

After running your application:

1. **Open Dashboard**: Navigate to [https://cloud.langfuse.com](https://cloud.langfuse.com)
2. **Select Project**: Choose your project from the sidebar
3. **View Traces**: Click on "Traces" to see all executions

### What You'll See:

- **Trace Timeline**: Visual representation of nested operations
- **Token Usage**: Input/output tokens per generation
- **Costs**: Calculated costs based on model pricing
- **Latency**: Time taken for each operation
- **Model Parameters**: Temperature, max_tokens, etc.
- **I/O Data**: Full prompts and completions
- **Metadata**: Custom tags and user information

## Common Issues & Solutions

### Issue: Traces Not Appearing

**Solution**: Ensure you call `langfuse.flush()` before script exits

```python
import atexit
atexit.register(lambda: langfuse.flush())
```

### Issue: Authentication Failed

**Solution**: Verify environment variables are set correctly

```python
import os
print(os.environ.get("LANGFUSE_PUBLIC_KEY"))
print(os.environ.get("LANGFUSE_HOST"))
```

### Issue: Missing Usage/Cost Data

**Solution**: Make sure model name matches Langfuse's model definitions, or add custom model:

```python
# In Langfuse dashboard: Settings → Models → Add Model
```

## Self-Hosting (Optional)

For self-hosting Langfuse:

```bash
# Clone repository
git clone https://github.com/langfuse/langfuse.git
cd langfuse

# Start with Docker Compose
docker compose up
```

Then set: `LANGFUSE_HOST="http://localhost:3000"`

## Additional Resources

- **Documentation**: [https://langfuse.com/docs](https://langfuse.com/docs)
- **GitHub**: [https://github.com/langfuse/langfuse](https://github.com/langfuse/langfuse)
- **Interactive Demo**: [https://langfuse.com/docs](https://langfuse.com/docs)
- **Discord Community**: Join for support and discussions

## Summary

Langfuse is a developer-first observability platform built specifically for LLM-powered applications, tracking prompts, responses, tool calls, costs, and latencies. It provides:

✅ **Multi-Provider Support**: Works with OpenAI, Anthropic, Azure, and 100+ models  
✅ **Easy Integration**: Simple decorators and context managers  
✅ **Cost Tracking**: Automatic token and cost calculation  
✅ **Nested Traces**: Visualize complex workflows  
✅ **Open Source**: Self-host or use managed cloud  
✅ **Framework Agnostic**: Works with LangChain, LlamaIndex, raw SDKs

Start building observable LLM applications today! 🚀
