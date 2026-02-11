"""
Demonstration of Top-k Retrieval vs Re-ranking
Using ChromaDB and LangChain
"""

import os
import shutil
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

from dotenv import load_dotenv
load_dotenv()

# Internal company documents - NOT general knowledge
# These are fictitious internal documents for AcmeCorp to demonstrate RAG
documents = [
    # HR & Benefits Documents
    Document(page_content="Q3 2024 Employee Benefits Update: The company has expanded mental health coverage to include 12 therapy sessions per year. Fertility treatment coverage increased to $25,000 lifetime maximum. Remote work stipend remains $500/quarter for home office equipment.", metadata={"category": "HR", "type": "benefits", "date": "2024-Q3"}),
    
    Document(page_content="Project Phoenix Retrospective - Post-Mortem Meeting Notes (Sept 15, 2024): The 6-month delay was caused primarily by third-party API integration issues with the legacy billing system. Team recommends microservices architecture for future projects. Sarah Chen led the backend refactoring effort.", metadata={"category": "engineering", "type": "retrospective", "project": "Phoenix", "date": "2024-09-15"}),
    
    Document(page_content="AcmeCorp Security Policy v2.3: All production database access requires approval from both the security team lead (currently Marcus Webb) and the VP of Engineering. Two-factor authentication mandatory for all cloud infrastructure. Password rotation required every 90 days.", metadata={"category": "security", "type": "policy", "version": "2.3"}),
    
    Document(page_content="Q3 Sales Pipeline Report: Enterprise deals worth $2.4M in total are expected to close in Q4. The HealthTech vertical showing 40% growth. Key accounts: St.Mary's Hospital system ($850K), Metro Transit Authority ($420K). Competitor analysis indicates we're losing ground to CompetitorX in the retail sector.", metadata={"category": "sales", "type": "report", "quarter": "Q3-2024"}),
    
    Document(page_content="Data Lake Architecture Spec - Engineering Doc: Current ingestion rate: 500GB/day from IoT sensors. Planning migration from AWS Redshift to Snowflake in January 2025. Estimated cost savings: $180K/year. Raja Patel is the technical lead for this initiative.", metadata={"category": "engineering", "type": "specification", "project": "DataLake"}),
    
    Document(page_content="Executive Committee Meeting Minutes (Oct 3, 2024): Approved budget increase of $500K for the European expansion. CFO raised concerns about Q3 cash burn rate of $1.2M. Board presentation scheduled for November 15. Discussion of potential Series C funding round.", metadata={"category": "executive", "type": "minutes", "date": "2024-10-03"}),
    
    Document(page_content="AcmeCorp 2024 Holiday Schedule: Company closed Dec 24-25, Dec 31-Jan 1. Floating holidays: 2 days to be used by end of Q1 2025. Martin Luther King Jr. Day observed on January 20, 2025. Note: Customer support team has modified schedule.", metadata={"category": "HR", "type": "policy", "year": "2024"}),
    
    Document(page_content="Customer Escalation Protocol - Tier 3 Support: Critical issues (P0) require 15-minute response time. Contact on-call engineer via PagerDuty. If unresolved in 2 hours, escalate to Director of Customer Success (currently Jennifer Walsh). SLA breach threshold: 99.9% uptime.", metadata={"category": "support", "type": "procedure", "version": "current"}),
    
    Document(page_content="Employee Performance Review Guidelines 2024: Reviews conducted bi-annually (June and December). 360-degree feedback required for Senior+ levels. Calibration sessions scheduled for Nov 12-14. Merit increases effective January 1, 2025. High performers eligible for stock option refresh.", metadata={"category": "HR", "type": "guidelines", "year": "2024"}),
    
    Document(page_content="Q3 Financial Results Summary: Revenue: $12.4M (+18% YoY). Net loss: $2.1M (improved from $3.2M in Q2). Cash runway: 14 months at current burn rate. Major expenses: Cloud infrastructure ($1.8M), Salaries ($4.2M), Marketing ($1.1M). Preparing for audit starting Nov 1.", metadata={"category": "finance", "type": "summary", "quarter": "Q3-2024"}),
    
    Document(page_content="Product Roadmap 2025 - Strategic Initiatives: Priority 1: AI-powered analytics dashboard (lead: Dr. Amara Singh). Priority 2: Mobile app redesign (lead: UX team under Jordan Lee). Priority 3: Real-time collaboration features. De-prioritized: Blockchain verification due to market demand analysis.", metadata={"category": "product", "type": "roadmap", "year": "2025"}),
    
    Document(page_content="Office Move Memo: Relocating from Building A to the new downtown headquarters on December 15, 2024. New address: 450 Innovation Drive, Suite 1200. IT equipment migration scheduled for weekend of Dec 14-15. Each employee allowed 2 boxes for personal items.", metadata={"category": "facilities", "type": "memo", "date": "2024-12-15"}),
]

# Initialize embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Vector store configuration
persist_dir = "./.chromadb/rerank_demo"

# Check if vector store already exists
if os.path.exists(persist_dir) and os.listdir(persist_dir):
    print(f"Loading existing vector store from {persist_dir}")
    vectorstore = Chroma(
        collection_name="rerank_demo_collection",
        embedding_function=embeddings,
        persist_directory=persist_dir
    )
else:
    print(f"Creating new vector store at {persist_dir}")
    # Clear any partial/corrupted data
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
    
    # Create vector store from documents
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="rerank_demo_collection",
        persist_directory=persist_dir
    )

query = "What are the benefits and compensation changes for employees in Q3 2024?"

print("=" * 80)
print("CASE 1: TOP-K RETRIEVAL (Standard Vector Similarity)")
print("=" * 80)

# Top-k retrieval: Get top 4 most similar documents based on vector similarity
top_k_results = vectorstore.similarity_search(query, k=4)

print(f"\nQuery: {query}\n")
print("Top-4 Results (ordered by cosine similarity):\n")
for i, doc in enumerate(top_k_results, 1):
    print(f"{i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content}")

print("\n" + "=" * 80)
print("CASE 2: RE-RANKING (Two-stage retrieval with custom scoring)")
print("=" * 80)

# Step 1: Get more candidates (top-k with larger k)
# This is called "recall" - cast a wider net
candidates = vectorstore.similarity_search(query, k=6)

print(f"\nStep 1: Initial retrieval (top-6 candidates):\n")
for i, doc in enumerate(candidates, 1):
    print(f"{i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content}")

# Step 2: Re-rank using a custom scoring function
# In practice, this would use a cross-encoder or more sophisticated model
# Here we'll simulate it with a simple keyword-based re-ranker

def rerank_score(doc, query):
    """
    Simple re-ranking function for internal company documents:
    - Keyword matching
    - Category relevance
    - Recency (date-based)
    
    In production, you'd use models like:
    - Cross-encoders (e.g., ms-marco-MiniLM)
    - BGE reranker
    - Cohere rerank API
    """
    score = 0.0
    content_lower = doc.page_content.lower()
    query_lower = query.lower()
    category = doc.metadata.get('category', 'unknown')
    
    # Keyword matching for employee benefits/compensation
    keywords = ["benefits", "compensation", "employee", "coverage", "stipend", "salary", "health", "insurance"]
    for keyword in keywords:
        if keyword in content_lower and keyword in query_lower:
            score += 2.0
        elif keyword in content_lower:
            score += 0.5
    
    # Bonus for HR-related documents
    if category == 'HR':
        score += 3.0
    
    # Bonus for benefits-specific documents
    if doc.metadata.get('type') == 'benefits':
        score += 2.0
    
    # Slight bonus for recent Q3 2024 documents
    if 'Q3' in doc.page_content or 'Q3-2024' in str(doc.metadata.get('quarter', '')):
        score += 1.0
    
    # Penalize technical/engineering docs for HR queries
    if category in ['engineering', 'security', 'product']:
        score -= 2.0
    
    return score

# Apply re-ranking
reranked = sorted(candidates, key=lambda doc: rerank_score(doc, query), reverse=True)

print(f"\nStep 2: Re-ranked results (top-4 after re-scoring):\n")
for i, doc in enumerate(reranked[:4], 1):
    score = rerank_score(doc, query)
    print(f"{i}. [score: {score:.1f}] [{doc.metadata.get('category', 'unknown')}] {doc.page_content}")

print("\n" + "=" * 80)
print("CASE 3: LANGCHAIN WITH COHERE RE-RANKER (Production Example)")
print("=" * 80)

print("\nNote: This is a production-ready example using Cohere's API.")
print("Requires: pip install langchain-cohere and COHERE_API_KEY environment variable\n")

# Base retriever (top-k with larger pool)
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

# Cohere re-ranker - requires COHERE_API_KEY to be set
try:
    compressor = CohereRerank(model="rerank-english-v3.0", top_n=4)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever
    )
    
    # Retrieve and re-rank
    cohere_results = compression_retriever.invoke(query)
    
    print("Step 1: Initial retrieval (top-6 candidates)")
    initial_candidates = base_retriever.invoke(query)
    for i, doc in enumerate(initial_candidates, 1):
        print(f"  {i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content[:50]}...")
    
    print(f"\nStep 2: Re-ranked results (top-4 after Cohere re-ranking):\n")
    for i, doc in enumerate(cohere_results, 1):
        print(f"{i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content}")
        
except Exception as e:
    print(f"Note: Cohere re-ranking skipped - {str(e)}")
    print("To use: Set COHERE_API_KEY environment variable and install langchain-cohere")

print("\n" + "=" * 80)
print("COMPARISON OF ALL THREE CASES")
print("=" * 80)

print("\nCase 1 - Top-k only:")
for i, doc in enumerate(top_k_results, 1):
    print(f"  {i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content[:50]}...")

print("\nCase 2 - With custom re-ranking:")
for i, doc in enumerate(reranked[:4], 1):
    print(f"  {i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content[:50]}...")

print("\nCase 3 - With Cohere re-ranking (if available):")
try:
    for i, doc in enumerate(cohere_results, 1):
        print(f"  {i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content[:50]}...")
except NameError:
    print("  (Results not available - Cohere API not configured)")

print("\n" + "=" * 80)
print("KEY DIFFERENCES SUMMARY")
print("=" * 80)

summary = """
Case 1 - Top-k Retrieval:
  - Single-stage process
  - Uses vector similarity (cosine, euclidean, etc.)
  - Fast but may miss semantic nuances
  - Returns k results based purely on embedding similarity
  
Case 2 - Custom Re-ranking:
  - Two-stage process
  - First: retrieve more candidates (e.g., top-6)
  - Second: apply custom scoring function
  - Slower but more accurate
  - Uses rule-based or heuristic scoring
  - Good for domain-specific ranking logic
  
Case 3 - Cohere Re-ranking (Production):
  - Production-ready neural re-ranking
  - Uses Cohere's rerank-english-v3.0 model
  - API-based: requires COHERE_API_KEY
  - Most accurate semantic understanding
  - Best for production RAG systems
  - Higher latency due to API call
  
When to use what:
  - Case 1 (Top-k alone): Speed matters, good enough accuracy
  - Case 2 (Custom re-ranking): Need custom domain logic, no external API
  - Case 3 (Cohere re-ranking): Production systems, best accuracy, API available
  - Combined approach: Standard RAG pattern (retrieve many, re-rank to best)
"""

print(summary)
