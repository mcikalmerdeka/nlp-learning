"""
Langfuse Multi-Provider LLM Observability Demo
===============================================
This script demonstrates Langfuse's LLM-agnostic observability capabilities
with multiple providers: OpenAI, Anthropic Claude, and using LiteLLM for broader support.

Requirements:
    pip install langfuse openai anthropic litellm opentelemetry-instrumentation-anthropic

Setup:
    1. Sign up at https://cloud.langfuse.com (free tier available)
    2. Get your Langfuse API keys from project settings
    3. Set environment variables or update the script below
"""

import os
from datetime import datetime

# ============================================================================
# CONFIGURATION - Set your API keys here or via environment variables
# ============================================================================

# Langfuse credentials (Get from https://cloud.langfuse.com)
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."  # Your public key
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."  # Your secret key
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"  # EU region
# os.environ["LANGFUSE_HOST"] = "https://us.cloud.langfuse.com"  # US region

# LLM Provider API Keys
os.environ["OPENAI_API_KEY"] = "sk-..."  # Your OpenAI key
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."  # Your Anthropic key

# ============================================================================
# Example 1: OpenAI with Langfuse Integration
# ============================================================================
print("=" * 80)
print("Example 1: OpenAI with Langfuse @observe decorator")
print("=" * 80)

from langfuse import observe
from langfuse.openai import openai  # Langfuse-wrapped OpenAI client


@observe()  # Automatically traces this function
def summarize_text_openai(text: str) -> str:
    """Summarize text using OpenAI GPT-4o"""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text concisely."},
            {"role": "user", "content": f"Summarize this: {text}"}
        ],
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].message.content


# Test OpenAI integration
test_text = "Langfuse is an open-source LLM engineering platform that provides observability, metrics, evaluations, and prompt management for AI applications."
result = summarize_text_openai(test_text)
print(f"OpenAI Summary: {result}\n")

# ============================================================================
# Example 2: Anthropic Claude with OpenTelemetry Instrumentation
# ============================================================================
print("=" * 80)
print("Example 2: Anthropic Claude with OpenTelemetry Instrumentation")
print("=" * 80)

from anthropic import Anthropic
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor
from langfuse import get_client

# Initialize Langfuse client
langfuse = get_client()

# Verify authentication
if langfuse.auth_check():
    print("✓ Langfuse client authenticated successfully!")
else:
    print("✗ Authentication failed. Check your credentials.")

# Auto-instrument Anthropic SDK calls
AnthropicInstrumentor().instrument()

anthropic_client = Anthropic()


@observe()
def analyze_sentiment_claude(text: str) -> str:
    """Analyze sentiment using Anthropic Claude"""
    with langfuse.start_as_current_generation(
        name="claude-sentiment-analysis",
        model="claude-sonnet-4-20250514",
        input=[{"role": "user", "content": text}]
    ) as generation:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": f"Analyze the sentiment of this text (positive, negative, or neutral): {text}"
                }
            ]
        )
        
        result = message.content[0].text
        
        # Update generation with output and usage
        generation.update(
            output=result,
            usage_details={
                "input": message.usage.input_tokens,
                "output": message.usage.output_tokens,
            }
        )
        
        return result


# Test Anthropic integration
result = analyze_sentiment_claude("Langfuse makes monitoring LLM applications incredibly easy and insightful!")
print(f"Claude Analysis: {result}\n")

# ============================================================================
# Example 3: Using Anthropic via OpenAI-compatible endpoint
# ============================================================================
print("=" * 80)
print("Example 3: Anthropic via OpenAI-compatible endpoint")
print("=" * 80)

from langfuse.openai import OpenAI

# Use Anthropic's OpenAI-compatible endpoint
anthropic_via_openai = OpenAI(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    base_url="https://api.anthropic.com/v1/"
)


@observe()
def translate_text_claude(text: str, target_language: str) -> str:
    """Translate text using Claude via OpenAI-compatible API"""
    response = anthropic_via_openai.chat.completions.create(
        model="claude-sonnet-4-20250514",
        messages=[
            {"role": "system", "content": f"You are a translator. Translate to {target_language}."},
            {"role": "user", "content": text}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content


result = translate_text_claude("Hello, how are you?", "Spanish")
print(f"Translation: {result}\n")

# ============================================================================
# Example 4: Multi-Provider Comparison with LiteLLM
# ============================================================================
print("=" * 80)
print("Example 4: Multi-Provider Comparison using LiteLLM")
print("=" * 80)

import litellm

# Configure LiteLLM to send logs to Langfuse
litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]


@observe()
def compare_models(prompt: str) -> dict:
    """Compare responses from multiple providers"""
    results = {}
    
    # OpenAI
    try:
        openai_response = litellm.completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            metadata={
                "provider": "openai",
                "trace_name": "multi-model-comparison"
            }
        )
        results["openai"] = openai_response.choices[0].message.content
    except Exception as e:
        results["openai"] = f"Error: {str(e)}"
    
    # Anthropic
    try:
        anthropic_response = litellm.completion(
            model="claude-sonnet-4-20250514",
            messages=[{"role": "user", "content": prompt}],
            metadata={
                "provider": "anthropic",
                "trace_name": "multi-model-comparison"
            }
        )
        results["anthropic"] = anthropic_response.choices[0].message.content
    except Exception as e:
        results["anthropic"] = f"Error: {str(e)}"
    
    return results


# Test multi-provider comparison
comparison_prompt = "Explain what observability means in AI applications in one sentence."
results = compare_models(comparison_prompt)

print("Model Comparison Results:")
for provider, response in results.items():
    print(f"\n{provider.upper()}:")
    print(f"  {response}")

# ============================================================================
# Example 5: Complex Workflow with Nested Traces
# ============================================================================
print("\n" + "=" * 80)
print("Example 5: Complex RAG-like Workflow with Nested Traces")
print("=" * 80)


@observe()
def retrieve_context(query: str) -> str:
    """Simulate document retrieval (RAG)"""
    # In a real app, this would query a vector database
    print(f"  → Retrieving context for: {query}")
    return "Langfuse provides comprehensive tracing, cost tracking, and evaluation features for LLM applications."


@observe()
def generate_answer(query: str, context: str) -> str:
    """Generate answer using retrieved context"""
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Answer based on this context: {context}"},
            {"role": "user", "content": query}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content


@observe()
def rag_pipeline(user_query: str) -> dict:
    """Complete RAG pipeline with nested traces"""
    print(f"Processing query: {user_query}")
    
    # Step 1: Retrieve context
    context = retrieve_context(user_query)
    
    # Step 2: Generate answer
    answer = generate_answer(user_query, context)
    
    print(f"  ← Answer generated: {answer[:100]}...")
    
    return {
        "query": user_query,
        "context": context,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    }


# Test RAG pipeline
rag_result = rag_pipeline("What features does Langfuse offer?")
print(f"\nFinal Answer: {rag_result['answer']}\n")

# ============================================================================
# Example 6: Manual Trace Creation (Advanced)
# ============================================================================
print("=" * 80)
print("Example 6: Manual Trace Creation with Custom Metadata")
print("=" * 80)


def custom_llm_call_with_manual_trace():
    """Demonstrate manual trace creation for custom scenarios"""
    with langfuse.start_as_current_span(
        name="custom-workflow",
        metadata={
            "environment": "production",
            "user_id": "demo_user_123",
            "feature": "custom_analysis"
        }
    ) as trace:
        
        # Step 1: Pre-processing
        with langfuse.start_as_current_span(name="preprocessing") as preprocess:
            print("  → Preprocessing input...")
            preprocess.update(output="Input preprocessed successfully")
        
        # Step 2: LLM Call
        with langfuse.start_as_current_generation(
            name="main-llm-call",
            model="gpt-4o-mini"
        ) as generation:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "What is machine learning?"}]
            )
            generation.update(output=response.choices[0].message.content)
        
        # Step 3: Post-processing
        with langfuse.start_as_current_span(name="postprocessing") as postprocess:
            print("  → Postprocessing output...")
            postprocess.update(output="Output formatted successfully")
        
        print("  ← Custom workflow completed")


custom_llm_call_with_manual_trace()

# ============================================================================
# Flush and View Results
# ============================================================================
print("\n" + "=" * 80)
print("Flushing traces to Langfuse...")
print("=" * 80)

# Ensure all traces are sent to Langfuse before script ends
langfuse.flush()

print("""
✓ All traces sent successfully!

View your traces at: https://cloud.langfuse.com

You should see:
  • Individual traces for each function call
  • Nested spans showing workflow hierarchy
  • Token usage and cost tracking
  • Model parameters and metadata
  • Performance metrics (latency, tokens/sec)

Key Features Demonstrated:
  1. ✓ OpenAI integration with @observe decorator
  2. ✓ Anthropic Claude with OpenTelemetry instrumentation
  3. ✓ Multi-provider support via OpenAI-compatible endpoints
  4. ✓ LiteLLM for unified multi-provider access
  5. ✓ Nested traces for complex workflows (RAG)
  6. ✓ Manual trace creation with custom metadata
  7. ✓ Automatic cost and usage tracking
  8. ✓ Provider-agnostic observability

Next Steps:
  • Explore the Langfuse dashboard
  • Set up evaluations and scoring
  • Create prompt management workflows
  • Build custom dashboards and alerts
""")
