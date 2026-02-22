[Sitemap](https://pub.towardsai.net/sitemap/sitemap.xml)
## [Towards AI](https://pub.towardsai.net/?source=post_page---publication_nav-98111c9905da-751135919d8e---------------------------------------)
·
Follow publication
# 5 Underrated Libraries & Frameworks for AI Engineers to Learn in 2026
[![Cikal Merdeka](https://miro.medium.com/v2/resize:fill:64:64/1*BM03U_eaeTWAdvqTiaQTMA.jpeg)](https://medium.com/@mcikalmerdeka?source=post_page---byline--751135919d8e---------------------------------------)
[Cikal Merdeka](https://medium.com/@mcikalmerdeka?source=post_page---byline--751135919d8e---------------------------------------)
Follow
8 min read
·
Jan 7, 2026
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fvote%2Ftowards-artificial-intelligence%2F751135919d8e&operation=register&redirect=https%3A%2F%2Fpub.towardsai.net%2F5-underrated-libraries-frameworks-for-ai-engineers-to-learn-in-2026-751135919d8e&user=Cikal+Merdeka&userId=d2aac873f6ac&source=---header_actions--751135919d8e---------------------clap_footer------------------)
40
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2F751135919d8e&operation=register&redirect=https%3A%2F%2Fpub.towardsai.net%2F5-underrated-libraries-frameworks-for-ai-engineers-to-learn-in-2026-751135919d8e&source=---header_actions--751135919d8e---------------------bookmark_footer------------------)
[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D751135919d8e&operation=register&redirect=https%3A%2F%2Fpub.towardsai.net%2F5-underrated-libraries-frameworks-for-ai-engineers-to-learn-in-2026-751135919d8e&source=---header_actions--751135919d8e---------------------post_audio_button------------------)
Share
![](https://miro.medium.com/v2/resize:fit:700/1*UongINJOyvipHG2duFCtTA.png)
In the fast-moving world of AI, we often get distracted by the flashiest models where everyone is talking about Gemini, GPT, Claude, or Grok models. But for AI Engineers building actual production systems, the model is just one small piece of a much larger complicated puzzle.
To build a robust AI application, you need to solve distinct engineering challenges: inference latency, observability, user interfaces, agentic orchestration, and memory management.
Here are 5 underrated libraries/frameworks (plus a bonus) that solve these specific architectural pain points that you can use in your projects.
## 1. llama.cpp: The CPU Inference Powerhouse
![](https://miro.medium.com/v2/resize:fit:700/1*verRpMuEtdeWMY2hR30JgQ.png)
### A. The Problem
For years, running modern Large Language Models (LLMs) came with a steep admission price: powerful, expensive NVIDIA GPUs. If you didn’t have massive VRAM (like me), you were stuck hitting APIs and paying per token. This created a huge barrier for local development, privacy-focused apps, and edge deployment.
### B. The Solution
[llama.cpp](https://github.com/ggml-org/llama.cpp) changed the game by proving you don’t need a dedicated GPU to run state-of-the-art models. It is a lightweight C++ inference engine that’s been deeply optimized to run blazingly fast on:
  * Apple Silicon Macs (using Metal GPU acceleration)
  * Standard CPUs (leveraging AVX SIMD instructions for parallel processing).


It allows you to run powerful models like Llama 3 or Mistral directly on your MacBook or budget server with surprisingly low latency.
In your architecture, this sits at the **Inference Runtime Layer** , replacing heavy frameworks like PyTorch when you just need to generate tokens efficiently.
### C. Example Code
This is the quick-setup code example of using the llama-cpp-python package and directly download the model from HuggingFace. You can directly copy and run this on Google Colab to see the results. As for the details on how to download in specific machine please refer to the official documentation.
```
# 1. Install required packages  
!pip install llama-cpp-python huggingface_hub  
  
# 2. Download the model from Hugging Face  
from huggingface_hub import hf_hub_download  
from llama_cpp import Llama  
  
model_path = hf_hub_download(  
    repo_id="unsloth/Qwen3-0.6B-GGUF",  
    filename="Qwen3-0.6B-Q4_K_M.gguf"  # Choose your quantization  
)  
  
# 3. Load and use the model  
llm = Llama(  
    model_path=model_path,   
    n_ctx=2048,   
    n_gpu_layers=-1  # Use GPU if available  
)  
  
# 4. Generate  
output = llm(  
    "Q: What is the capital of France? A:",   
    max_tokens=128,   
    stop=["\n"],   
    echo=False  
)  
  
print(output["choices"][0]["text"])
```

Note: Why GGUF format? **GGUF (GPT-Generated Unified Format)** is llama.cpp’s custom model format because:
1. Quantization Support
  * Standard models (PyTorch `.bin`, Safetensors) use full precision (float32/float16)
  * GGUF supports aggressive quantization: Q4, Q5, Q8 (4-bit, 5-bit, 8-bit)
  * Example: A 7B model goes from 14GB → 4GB with Q4 quantization


2. Optimized Memory Layout
  * GGUF organizes data specifically for llama.cpp’s inference engine
  * Enables fast loading and efficient memory access patterns
  * Metadata embedded in the file (vocabulary, architecture, etc.)


3. Cross-Platform Compatibility
  * Single file format works on Windows, Mac, Linux, mobile
  * No Python dependencies needed at inference time


### D. The Verdict
Use this when you need low-cost, offline, or private inference on consumer hardware. Just remember that while it’s a miracle for CPUs, it won’t beat the raw batch-processing throughput of vLLM on an H100 cluster.
## 2. Langfuse: X-Ray Vision for Your LLM Stack
![](https://miro.medium.com/v2/resize:fit:700/1*9T7BCFKXLFg85wMaAfdJeA.png)
Weirdly enough the first time I knew about this tool, the name remind me of the famous framework of Langchain ecosystem (Langchain-Langgraph-Langsmith) since they are similar so I thought it was part of them, but this is actually different service.
### A. The Problem
Building with LLMs is often non-deterministic. You send a prompt, and sometimes you get a perfect answer, other times a hallucination. When your app breaks in production, traditional tools like Datadog don’t tell you why they just see a successful HTTP 200 OK. You’re left guessing which part of your prompt chain failed.
### B. The Solution
[Langfuse](https://langfuse.com/) is an open-source observability platform designed specifically for this “black box” problem. It captures the full trace of your AI application — inputs, outputs, latency, and costs per step. It gives you X-Ray vision into your stack, allowing you to see exactly what happened inside every retrieval step and LLM call.
It fits into the **Observability & MLOps Layer**, wrapping your application logic to provide deep visibility into agent behavior and RAG pipelines.
### C. Example Code
```
from langfuse.decorators import observe  
  
@observe() # Automatically captures inputs, outputs, and errors  
def story_generator(topic):  
    # If the LLM hallucinates here, you'll see the exact prompt and response in the dash  
    return llm.run(f"Write a story about {topic}")  
  
story_generator("The future of coding")
```

### D. The Verdict
If you are moving beyond a simlpe agent with tool prototype, this is mandatory. The only trade-off is the data volume; tracing every token in a high-traffic app generates a lot of logs, so you’ll need to manage your self-hosted instance carefully or use their cloud tier.
## 3. Gradio: UIs for Backend Engineers
![](https://miro.medium.com/v2/resize:fit:700/1*-QbOTDYSJuV_ecseiaQgWQ.png)
### A. The Problem
AI Engineers are typically great at Python and models, but often struggle with modern frontend stacks like React or Vue. However, you can’t ship a model if stakeholders can’t touch it. Building a custom UI just to demo a prototype is a massive time sink that distracts from the actual modeling work.
### B. The Solution
[Gradio](https://www.gradio.app/docs) bridges this gap by allowing you to generate robust, interactive web interfaces entirely in Python. It’s not just for simple inputs; it handles audio, images, and chat interfaces out of the box. It turns a Python function into a shareable web app in literally three lines of code.
## Get Cikal Merdeka’s stories in your inbox
Join Medium for free to get updates from this writer.
Subscribe
Subscribe
This lives in the **Presentation Layer** , serving as the fastest way to get a human-in-the-loop approach for testing or internal tooling.
There is other alternative which is already quite famous for years in demoing an traditional ML and data science applications before called [Streamlit](https://streamlit.io/), but I think learning Gradio is a great investment since most of the LLM applications deployed in HuggingFace demos are mostly in Gradio interface also, since it’s quite straightforward to use.
### C. Example Code (using OpenAI model for the LLM)
```
import gradio as gr  
from openai import OpenAI  
  
client = OpenAI()  
  
def analyze_sentiment(text):  
    response = client.chat.completions.create(  
        model="gpt-4o-mini",  
        messages=[{"role": "user", "content": f"Analyze sentiment: {text}"}]  
    )  
    return response.choices[0].message.content  
  
# Creates a full web UI with text box and output display  
demo = gr.Interface(fn=analyze_sentiment, inputs="text", outputs="text")  
demo.launch()
```

### D. The Verdict
Use Gradio for internal tools, rapid prototyping, and demos. It’s incredibly fast to build. Just avoid using it for your main consumer-facing landing page since it’s designed for utility, not pixel-perfect custom branding.
## 4. Agno: Agents without the Headache
![](https://miro.medium.com/v2/resize:fit:531/1*cMlUCAg-ao_0Dedahr-wQA.png)
### A. The Problem
Agentic AI is the current hype, but frameworks like LangChain have become incredibly complex, forcing developers into rigid abstractions and confusing graph structures. Debugging a massive graph of chains when your agent gets stuck is a nightmare.
### B. The Solution
[Agno](https://www.agno.com/) (a rebranding of the popular _Phidata_) takes a different approach: **simplicity**. It frameworks agents as simple, clean Python objects. It focuses on giving agents tools (like web search or database access) and memory without the massive boilerplate. It’s “code-first” rather than “graph-first” approach.
It sits in the **Orchestration Layer** , acting as the brain that directs your LLM to perform actions in the real world.
### C. Example Code
```
from agno.agent import Agent  
from agno.models.openai import OpenAIChat  
from agno.tools.duckduckgo import DuckDuckGo  
  
# An agent that natively understands tools without complex chains  
agent = Agent(  
    model=OpenAIChat(id="gpt-4o"),  
    description="You are a financial analyst",  
    instructions=["Always use tables to display data"],  
    tools=[DuckDuckGo()],  
    markdown=True  
)  
  
# The agent decides autonomously to use tools (like searching the web) if needed  
agent.print_response("What is the stock price of NVDA?", stream=True)
```

### D. The Verdict
If you want to build autonomous agents and want to understand the code you are writing, Agno is a breath of fresh air. It’s perfect for developers who prefer lightweight and understandable over comprehensive but bloated.
## 5. FAISS: The Engine of Long-Term Memory
### A. The Problem
In RAG (Retrieval Augmented Generation) systems, you often have to search through millions of document chunks to find the relevant context. Doing this with a simple loop is agonizingly slow. You need a way to find similar things instantly, even in massive datasets.
### B. The Solution
[FAISS](https://ai.meta.com/tools/faiss/) (Facebook AI Similarity Search) is the industry standard for this. It’s a library that implements efficient algorithms for searching and clustering dense vectors. It essentially gives your AI Long Term Memory that can be queried in milliseconds, regardless of how much data you have.
This is the core of your **Retrieval Layer** , powering the backend of almost every scalable RAG application.
> Important: FAISS is not a full vector database like Pinecone, Qdrant, or Weaviate. It’s a low-level library, a powerful algorithmic toolkit that you integrate into your application. It doesn’t offer built-in persistence, CRUD operations, metadata filtering, or multi-node clustering out of the box. Instead, it’s the _engine_ that many complete vector databases use under the hood.
### C. Example Code (combined with Langchain)
```
from langchain_community.vectorstores import FAISS  
from langchain_openai import OpenAIEmbeddings  
  
# Assuming 'docs' is a list of Document objects  
embeddings = OpenAIEmbeddings()  
db = FAISS.from_documents(docs, embeddings)  
  
# Perform a similarity search  
query = "What is the main topic of the document?"  
found_docs = db.similarity_search(query)  
  
print(found_docs[0].page_content)
```

### D. The Verdict
Use FAISS when performance fits. It’s low-level and powerful. However, if you are just starting with a few hundred documents, it might be overkill, sometimes a simple list is enough. But for scale, FAISS is a great alternative to consider.
## 6. (Bonus) Redis: The Conversation Short-Term Memory
![](https://miro.medium.com/v2/resize:fit:700/1*elPZSlLHt1ObHeklNQDqgA.png)
### A. The Problem
Stateless APIs are great for servers, but terrible for chatbots. An AI needs to remember what you said two seconds ago. Storing this chat history in a traditional database (like SQL) adds unnecessary latency to every single interaction.
### B. The Solution
[Redis](https://redis.io/) is the perfect solution for Short Term Memory. As an in-memory data store, it reads and writes in sub-milliseconds. It allows you to store active user sessions, chat history, and cache frequent LLM responses to save money.
### C. Example Code (combined with Langchain)
```
import redis  
from langchain_openai import ChatOpenAI  
from langchain_redis import RedisChatMessageHistory  
  
# Initialize Redis client  
redis_client = redis.Redis(host="localhost", port=6379, db=0)  
  
# Get chat history for a specific session  
def get_chat_history(session_id: str):  
    return RedisChatMessageHistory(session_id=session_id, redis_client=redis_client)  
  
# Use it in your chatbot  
history = get_chat_history("user_123")  
history.add_user_message("What's the weather?")  
history.add_ai_message("It's sunny today!")  
  
# Retrieve all messages instantly  
messages = history.messages
```

### D. The Verdict
For any chat interface that needs to feel snappy and aware, Redis is the standard choice. Don’t use your cold storage database for hot conversation state.
## Closing Thoughts
The best AI engineers aren’t just prompt engineers; they are system architecture engineers. They know that llama.cpp handles the run, Langfuse watches the run, Gradio shows the run, Agno orchestrate the run, FAISS remembers the past, and lastly Redis remembers the now.
Mastering these tools moves you from scripting with an API to architecting systems.
#ArtificialIntelligence #MachineLearning #AI #LLM #VectorDatabase #AgenticAI #SoftwareEngineering #Python #LlamaCpp #Langfuse #Gradio #Agno #FAISS #Redis #RAG #LLMOps
[Artificial Intelligence](https://medium.com/tag/artificial-intelligence?source=post_page-----751135919d8e---------------------------------------)
[Agentic Ai](https://medium.com/tag/agentic-ai?source=post_page-----751135919d8e---------------------------------------)
[LLM](https://medium.com/tag/llm?source=post_page-----751135919d8e---------------------------------------)
[Software Engineering](https://medium.com/tag/software-engineering?source=post_page-----751135919d8e---------------------------------------)
[Machine Learning](https://medium.com/tag/machine-learning?source=post_page-----751135919d8e---------------------------------------)
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fvote%2Ftowards-artificial-intelligence%2F751135919d8e&operation=register&redirect=https%3A%2F%2Fpub.towardsai.net%2F5-underrated-libraries-frameworks-for-ai-engineers-to-learn-in-2026-751135919d8e&user=Cikal+Merdeka&userId=d2aac873f6ac&source=---footer_actions--751135919d8e---------------------clap_footer------------------)
40
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fvote%2Ftowards-artificial-intelligence%2F751135919d8e&operation=register&redirect=https%3A%2F%2Fpub.towardsai.net%2F5-underrated-libraries-frameworks-for-ai-engineers-to-learn-in-2026-751135919d8e&user=Cikal+Merdeka&userId=d2aac873f6ac&source=---footer_actions--751135919d8e---------------------clap_footer------------------)
40
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2F751135919d8e&operation=register&redirect=https%3A%2F%2Fpub.towardsai.net%2F5-underrated-libraries-frameworks-for-ai-engineers-to-learn-in-2026-751135919d8e&source=---footer_actions--751135919d8e---------------------bookmark_footer------------------)
[![Towards AI](https://miro.medium.com/v2/resize:fill:96:96/1*JyIThO-cLjlChQLb6kSlVQ.png)](https://pub.towardsai.net/?source=post_page---post_publication_info--751135919d8e---------------------------------------)
[![Towards AI](https://miro.medium.com/v2/resize:fill:128:128/1*JyIThO-cLjlChQLb6kSlVQ.png)](https://pub.towardsai.net/?source=post_page---post_publication_info--751135919d8e---------------------------------------)
Follow
## [Published in Towards AI](https://pub.towardsai.net/?source=post_page---post_publication_info--751135919d8e---------------------------------------)
[110K followers](https://pub.towardsai.net/followers?source=post_page---post_publication_info--751135919d8e---------------------------------------)
·[Last published just now](https://pub.towardsai.net/the-outlier-and-feature-selection-dilemma-preparing-data-for-clustering-ebf228b5810c?source=post_page---post_publication_info--751135919d8e---------------------------------------)
We build Enterprise AI. We teach what we learn. Join 100K+ AI practitioners on Towards AI Academy. Free: 6-day Agentic AI Engineering Email Guide: <https://email-course.towardsai.net/>
Follow
[![Cikal Merdeka](https://miro.medium.com/v2/resize:fill:96:96/1*BM03U_eaeTWAdvqTiaQTMA.jpeg)](https://medium.com/@mcikalmerdeka?source=post_page---post_author_info--751135919d8e---------------------------------------)
[![Cikal Merdeka](https://miro.medium.com/v2/resize:fill:128:128/1*BM03U_eaeTWAdvqTiaQTMA.jpeg)](https://medium.com/@mcikalmerdeka?source=post_page---post_author_info--751135919d8e---------------------------------------)
Follow
## [Written by Cikal Merdeka](https://medium.com/@mcikalmerdeka?source=post_page---post_author_info--751135919d8e---------------------------------------)
[13 followers](https://medium.com/@mcikalmerdeka/followers?source=post_page---post_author_info--751135919d8e---------------------------------------)
·[10 following](https://medium.com/@mcikalmerdeka/following?source=post_page---post_author_info--751135919d8e---------------------------------------)
AI Engineering | Data Scientist | Data Analyst | AI and NLP Enthusiast. - Github: [github.com/mcikalmerdeka](http://github.com/mcikalmerdeka) - Website: [mcikalmerdeka.vercel.app](http://mcikalmerdeka.vercel.app)
Follow
## No responses yet
[](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page---post_responses--751135919d8e---------------------------------------)
![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)
Write a response
[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fpub.towardsai.net%2F5-underrated-libraries-frameworks-for-ai-engineers-to-learn-in-2026-751135919d8e&source=---post_responses--751135919d8e---------------------respond_sidebar------------------)
Cancel
Respond
## More from Cikal Merdeka and Towards AI
![Building Your First AI Agent with LangChain: A Complete Practical Guide](https://miro.medium.com/v2/resize:fit:679/format:webp/1*Ab7vmRhEnXTwbZV3GqDiyQ.png)
[![Artificial Intelligence in Plain English](https://miro.medium.com/v2/resize:fill:20:20/1*9zAmnK08gUCmZX7q0McVKw@2x.png)](https://ai.plainenglish.io/?source=post_page---author_recirc--751135919d8e----0---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
In
[Artificial Intelligence in Plain English](https://ai.plainenglish.io/?source=post_page---author_recirc--751135919d8e----0---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
by
[Cikal Merdeka](https://medium.com/@mcikalmerdeka?source=post_page---author_recirc--751135919d8e----0---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
## [Building Your First AI Agent with LangChain: A Complete Practical Guide Introduction](https://ai.plainenglish.io/building-your-first-ai-agent-with-langchain-a-complete-practical-guide-e5b3deb7f109?source=post_page---author_recirc--751135919d8e----0---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
Oct 19, 2025
[](https://ai.plainenglish.io/building-your-first-ai-agent-with-langchain-a-complete-practical-guide-e5b3deb7f109?source=post_page---author_recirc--751135919d8e----0---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2Fe5b3deb7f109&operation=register&redirect=https%3A%2F%2Fai.plainenglish.io%2Fbuilding-your-first-ai-agent-with-langchain-a-complete-practical-guide-e5b3deb7f109&source=---author_recirc--751135919d8e----0-----------------bookmark_preview----d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
![I Cancelled My ~$200/mo Claude API Subscription, Again.](https://miro.medium.com/v2/resize:fit:679/format:webp/1*HFBl5SZUNoGWx00imA2c3A.png)
[![Towards AI](https://miro.medium.com/v2/resize:fill:20:20/1*JyIThO-cLjlChQLb6kSlVQ.png)](https://pub.towardsai.net/?source=post_page---author_recirc--751135919d8e----1---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
In
[Towards AI](https://pub.towardsai.net/?source=post_page---author_recirc--751135919d8e----1---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
by
[Adham Khaled](https://medium.com/@adham__khaled__?source=post_page---author_recirc--751135919d8e----1---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
## [I Cancelled My ~$200/mo Claude API Subscription, Again. Kimi K2.5 didn’t just lower the price. It destroyed the business model of “renting intelligence.”](https://pub.towardsai.net/i-cancelled-my-200-mo-claude-api-subscription-again-0e2175502778?source=post_page---author_recirc--751135919d8e----1---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
Feb 9
[ A response icon56 ](https://pub.towardsai.net/i-cancelled-my-200-mo-claude-api-subscription-again-0e2175502778?source=post_page---author_recirc--751135919d8e----1---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2F0e2175502778&operation=register&redirect=https%3A%2F%2Fpub.towardsai.net%2Fi-cancelled-my-200-mo-claude-api-subscription-again-0e2175502778&source=---author_recirc--751135919d8e----1-----------------bookmark_preview----d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
![Close-up of crumpled resignation letter reading “The world is in peril” on glass desk](https://miro.medium.com/v2/resize:fit:679/format:webp/1*soOdcGJUttkxAtRblQEMCg.png)
[![Towards AI](https://miro.medium.com/v2/resize:fill:20:20/1*JyIThO-cLjlChQLb6kSlVQ.png)](https://pub.towardsai.net/?source=post_page---author_recirc--751135919d8e----2---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
In
[Towards AI](https://pub.towardsai.net/?source=post_page---author_recirc--751135919d8e----2---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
by
[MohamedAbdelmenem](https://medium.com/@mohamed-abdelmenem?source=post_page---author_recirc--751135919d8e----2---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
## [They Built the AI. Now They’re Quitting. Here’s What They Saw. Matt Shumer’s essay hit 75M views. xAI’s co-founder quit citing “recursive self-improvement.” Microsoft’s AI chief says 18 months. Here’s…](https://pub.towardsai.net/they-built-the-ai-now-theyre-quitting-here-s-what-they-saw-c62a0f33f8dc?source=post_page---author_recirc--751135919d8e----2---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
Feb 15
[ A response icon140 ](https://pub.towardsai.net/they-built-the-ai-now-theyre-quitting-here-s-what-they-saw-c62a0f33f8dc?source=post_page---author_recirc--751135919d8e----2---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2Fc62a0f33f8dc&operation=register&redirect=https%3A%2F%2Fpub.towardsai.net%2Fthey-built-the-ai-now-theyre-quitting-here-s-what-they-saw-c62a0f33f8dc&source=---author_recirc--751135919d8e----2-----------------bookmark_preview----d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
![Context Engineering: The Essential Skill for the AI Orchestration Era](https://miro.medium.com/v2/resize:fit:679/format:webp/1*aTHQOke3bM6SVMQ6deWZMg.png)
[![Towards AI](https://miro.medium.com/v2/resize:fill:20:20/1*JyIThO-cLjlChQLb6kSlVQ.png)](https://pub.towardsai.net/?source=post_page---author_recirc--751135919d8e----3---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
In
[Towards AI](https://pub.towardsai.net/?source=post_page---author_recirc--751135919d8e----3---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
by
[Cikal Merdeka](https://medium.com/@mcikalmerdeka?source=post_page---author_recirc--751135919d8e----3---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
## [Context Engineering: The Essential Skill for the AI Orchestration Era If you’ve been building with LLMs, you’ve probably experienced this: you craft the perfect prompt, your model gives great responses in…](https://pub.towardsai.net/context-engineering-the-essential-skill-for-the-ai-orchestration-era-a2ae425797e1?source=post_page---author_recirc--751135919d8e----3---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
Jan 21
[](https://pub.towardsai.net/context-engineering-the-essential-skill-for-the-ai-orchestration-era-a2ae425797e1?source=post_page---author_recirc--751135919d8e----3---------------------d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2Fa2ae425797e1&operation=register&redirect=https%3A%2F%2Fpub.towardsai.net%2Fcontext-engineering-the-essential-skill-for-the-ai-orchestration-era-a2ae425797e1&source=---author_recirc--751135919d8e----3-----------------bookmark_preview----d3ed1676_a230_4e24_9be2_1aecdfee8f86--------------)
[See all from Cikal Merdeka](https://medium.com/@mcikalmerdeka?source=post_page---author_recirc--751135919d8e---------------------------------------)
[See all from Towards AI](https://pub.towardsai.net/?source=post_page---author_recirc--751135919d8e---------------------------------------)
## Recommended from Medium
![Why the Smartest People in Tech Are Quietly Panicking Right Now](https://miro.medium.com/v2/resize:fit:679/format:webp/1*W96wtREHKtBU9qvqSJkovw.png)
[![Activated Thinker](https://miro.medium.com/v2/resize:fill:20:20/1*I0dmd2-TIrUdjo5eUTjtvw.png)](https://medium.com/activated-thinker?source=post_page---read_next_recirc--751135919d8e----0---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
In
[Activated Thinker](https://medium.com/activated-thinker?source=post_page---read_next_recirc--751135919d8e----0---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
by
[Shane Collins](https://medium.com/@intellizab?source=post_page---read_next_recirc--751135919d8e----0---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
## [Why the Smartest People in Tech Are Quietly Panicking Right Now The water is rising fast, and your free version of ChatGPT is hiding the terrifying, exhilarating truth](https://medium.com/activated-thinker/why-the-smartest-people-in-tech-are-quietly-panicking-right-now-d2feb86e7e4b?source=post_page---read_next_recirc--751135919d8e----0---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
Feb 13
[ A response icon391 ](https://medium.com/activated-thinker/why-the-smartest-people-in-tech-are-quietly-panicking-right-now-d2feb86e7e4b?source=post_page---read_next_recirc--751135919d8e----0---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2Fd2feb86e7e4b&operation=register&redirect=https%3A%2F%2Fmedium.com%2Factivated-thinker%2Fwhy-the-smartest-people-in-tech-are-quietly-panicking-right-now-d2feb86e7e4b&source=---read_next_recirc--751135919d8e----0-----------------bookmark_preview----bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
![21 OpenClaw Automations Nobody Talks About — Because the Obvious Ones Already Broke the Internet](https://miro.medium.com/v2/resize:fit:679/format:webp/0*1zBRF29ZHl0XB6WA.png)
[![Phil | Rentier Digital Automation](https://miro.medium.com/v2/resize:fill:20:20/1*8_UYeI21v_IBgt9VUGxsPg.png)](https://medium.com/@rentierdigital?source=post_page---read_next_recirc--751135919d8e----1---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
[Phil | Rentier Digital Automation](https://medium.com/@rentierdigital?source=post_page---read_next_recirc--751135919d8e----1---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
## [21 OpenClaw Automations Nobody Talks About — Because the Obvious Ones Already Broke the Internet After I published “33 OpenClaw Automations,” my DMs exploded. Not with compliments — with questions. The same question, over and over…](https://medium.com/@rentierdigital/21-openclaw-automations-nobody-talks-about-because-the-obvious-ones-already-broke-the-internet-3f881b9e0018?source=post_page---read_next_recirc--751135919d8e----1---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
Feb 15
[ A response icon8 ](https://medium.com/@rentierdigital/21-openclaw-automations-nobody-talks-about-because-the-obvious-ones-already-broke-the-internet-3f881b9e0018?source=post_page---read_next_recirc--751135919d8e----1---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2F3f881b9e0018&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40rentierdigital%2F21-openclaw-automations-nobody-talks-about-because-the-obvious-ones-already-broke-the-internet-3f881b9e0018&source=---read_next_recirc--751135919d8e----1-----------------bookmark_preview----bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
![25 LLM Best Practices I Believe Every Engineer Should Learn Early](https://miro.medium.com/v2/resize:fit:679/format:webp/1*lkIFyo_Ls2ZYGTkqGq0FmA.png)
[![Towards AI](https://miro.medium.com/v2/resize:fill:20:20/1*JyIThO-cLjlChQLb6kSlVQ.png)](https://pub.towardsai.net/?source=post_page---read_next_recirc--751135919d8e----0---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
In
[Towards AI](https://pub.towardsai.net/?source=post_page---read_next_recirc--751135919d8e----0---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
by
[Khushbu Shah](https://medium.com/@khushbu.shah_661?source=post_page---read_next_recirc--751135919d8e----0---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
## [25 LLM Best Practices I Believe Every Engineer Should Learn Early Anyone can get an LLM to respond. Making it respond correctly every time is engineering. These LLM best practices will help you turn models…](https://pub.towardsai.net/25-llm-best-practices-i-believe-every-engineer-should-learn-early-259ce970e06c?source=post_page---read_next_recirc--751135919d8e----0---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
[ A response icon1 ](https://pub.towardsai.net/25-llm-best-practices-i-believe-every-engineer-should-learn-early-259ce970e06c?source=post_page---read_next_recirc--751135919d8e----0---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2F259ce970e06c&operation=register&redirect=https%3A%2F%2Fpub.towardsai.net%2F25-llm-best-practices-i-believe-every-engineer-should-learn-early-259ce970e06c&source=---read_next_recirc--751135919d8e----0-----------------bookmark_preview----bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
![Designing efficient Agentic AI Workflows](https://miro.medium.com/v2/resize:fit:679/format:webp/1*PFs7xcYsnE0YuhRTj96wiw.png)
[![AI Advances](https://miro.medium.com/v2/resize:fill:20:20/1*R8zEd59FDf0l8Re94ImV0Q.png)](https://ai.gopubby.com/?source=post_page---read_next_recirc--751135919d8e----1---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
In
[AI Advances](https://ai.gopubby.com/?source=post_page---read_next_recirc--751135919d8e----1---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
by
[Debmalya Biswas](https://debmalyabiswas.medium.com/?source=post_page---read_next_recirc--751135919d8e----1---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
## [Designing efficient Agentic AI Workflows Agentification UI/UX: Mapping Enterprise Processes to Agentic Execution Graphs](https://ai.gopubby.com/why-designing-efficient-agentic-ai-workflows-is-so-hard-f6ceb07496aa?source=post_page---read_next_recirc--751135919d8e----1---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
Feb 9
[ A response icon8 ](https://ai.gopubby.com/why-designing-efficient-agentic-ai-workflows-is-so-hard-f6ceb07496aa?source=post_page---read_next_recirc--751135919d8e----1---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2Ff6ceb07496aa&operation=register&redirect=https%3A%2F%2Fai.gopubby.com%2Fwhy-designing-efficient-agentic-ai-workflows-is-so-hard-f6ceb07496aa&source=---read_next_recirc--751135919d8e----1-----------------bookmark_preview----bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
![Why Thousands Are Buying Mac Minis to Escape Big Tech AI Subscriptions Forever | Clawdbot](https://miro.medium.com/v2/resize:fit:679/format:webp/1*YZcveDctIOQ2Zsf2z2_Ztg.png)
[![CodeX](https://miro.medium.com/v2/resize:fill:20:20/1*VqH0bOrfjeUkznphIC7KBg.png)](https://medium.com/codex?source=post_page---read_next_recirc--751135919d8e----2---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
In
[CodeX](https://medium.com/codex?source=post_page---read_next_recirc--751135919d8e----2---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
by
[MayhemCode](https://medium.com/@mayhemcode?source=post_page---read_next_recirc--751135919d8e----2---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
## [Why Thousands Are Buying Mac Minis to Escape Big Tech AI Subscriptions Forever | Clawdbot Something strange happened in early 2026. Apple stores started running low on Mac Minis. Tech forums exploded with setup guides. Developers…](https://medium.com/codex/why-thousands-are-buying-mac-minis-to-escape-big-tech-ai-subscriptions-forever-clawdbot-10c970c72404?source=post_page---read_next_recirc--751135919d8e----2---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
Feb 15
[ A response icon13 ](https://medium.com/codex/why-thousands-are-buying-mac-minis-to-escape-big-tech-ai-subscriptions-forever-clawdbot-10c970c72404?source=post_page---read_next_recirc--751135919d8e----2---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2F10c970c72404&operation=register&redirect=https%3A%2F%2Fmedium.com%2Fcodex%2Fwhy-thousands-are-buying-mac-minis-to-escape-big-tech-ai-subscriptions-forever-clawdbot-10c970c72404&source=---read_next_recirc--751135919d8e----2-----------------bookmark_preview----bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
![Musk Just Started The Walkback Of The Century](https://miro.medium.com/v2/resize:fit:679/format:webp/0*frwEQHWphxG5iRHa)
[![Will Lockett](https://miro.medium.com/v2/resize:fill:20:20/1*V0qWMQ8V5_NaF9yUoHAdyg.jpeg)](https://wlockett.medium.com/?source=post_page---read_next_recirc--751135919d8e----3---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
[Will Lockett](https://wlockett.medium.com/?source=post_page---read_next_recirc--751135919d8e----3---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
## [Musk Just Started The Walkback Of The Century Overpromise and underdeliver, yet again.](https://wlockett.medium.com/musk-just-started-the-walkback-of-the-century-17e5000a583b?source=post_page---read_next_recirc--751135919d8e----3---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
[ A response icon107 ](https://wlockett.medium.com/musk-just-started-the-walkback-of-the-century-17e5000a583b?source=post_page---read_next_recirc--751135919d8e----3---------------------bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
[](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2F_%2Fbookmark%2Fp%2F17e5000a583b&operation=register&redirect=https%3A%2F%2Fwlockett.medium.com%2Fmusk-just-started-the-walkback-of-the-century-17e5000a583b&source=---read_next_recirc--751135919d8e----3-----------------bookmark_preview----bcb5c469_22b4_41a4_a271_ef42433c830e--------------)
[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--751135919d8e---------------------------------------)
[Help](https://help.medium.com/hc/en-us?source=post_page-----751135919d8e---------------------------------------)
[Status](https://status.medium.com/?source=post_page-----751135919d8e---------------------------------------)
[About](https://medium.com/about?autoplay=1&source=post_page-----751135919d8e---------------------------------------)
[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----751135919d8e---------------------------------------)
Press
[Blog](https://blog.medium.com/?source=post_page-----751135919d8e---------------------------------------)
[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----751135919d8e---------------------------------------)
[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----751135919d8e---------------------------------------)
[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----751135919d8e---------------------------------------)
[Text to speech](https://speechify.com/medium?source=post_page-----751135919d8e---------------------------------------)
![Cikal Merdeka's profile picture](https://miro.medium.com/v2/resize:fill:48:48/1*BM03U_eaeTWAdvqTiaQTMA.jpeg)
## Be the first to hear about new stories from Cikal Merdeka
#### Join Medium for free to get updates from Cikal Merdeka sent right to your inbox.
Your email
Create account
Other sign up options
Already have an account? Sign in
By clicking "Create Account", you accept Medium's [Terms of Service](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=register-----751135919d8e-----------------d2aac873f6ac----subscribe_to_author------------------) and [Privacy Policy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=register-----751135919d8e-----------------d2aac873f6ac----subscribe_to_author------------------).
This site uses reCaptcha and the Google [Privacy Policy](https://policies.google.com/privacy?source=register-----751135919d8e-----------------d2aac873f6ac----subscribe_to_author------------------) and [Terms of Service](https://policies.google.com/terms?source=register-----751135919d8e-----------------d2aac873f6ac----subscribe_to_author------------------) apply.
