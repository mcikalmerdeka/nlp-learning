"""
Hybrid Search Demonstration
============================
Combining Vector Similarity + BM25 (Keyword) for improved retrieval.
Using ChromaDB, OpenAI Embeddings, and LangChain.
"""

import os
import shutil
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from rank_bm25 import BM25Okapi
import numpy as np

from dotenv import load_dotenv
load_dotenv()

# Internal company documents - NOT general knowledge
# These are fictitious internal documents for AcmeCorp to demonstrate Hybrid Search
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

# Initialize embeddings (OpenAI - same as topk_vs_reranking.py)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Vector store configuration
persist_dir = "./.chromadb/hybrid_search"

# Check if vector store already exists
if os.path.exists(persist_dir) and os.listdir(persist_dir):
    print(f"Loading existing vector store from {persist_dir}")
    vectorstore = Chroma(
        collection_name="hybrid_search_collection",
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
        collection_name="hybrid_search_collection",
        persist_directory=persist_dir
    )

query = "What are the benefits and compensation changes for employees in Q3 2024?"

print("=" * 80)
print("CASE 1: STANDARD VECTOR SEARCH")
print("=" * 80)

# Standard vector-only retrieval
vector_results = vectorstore.similarity_search(query, k=4)

print(f"\nQuery: {query}\n")
print("Vector-only results (top-4):")
for i, doc in enumerate(vector_results, 1):
    print(f"{i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content}")

print("\n" + "=" * 80)
print("CASE 2: HYBRID SEARCH (Vector + BM25 with EnsembleRetriever)")
print("=" * 80)

# Create BM25 retriever (keyword-based)
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 6  # Retrieve more candidates for hybrid

# Create vector retriever
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

# Combine both with weights
# 0.5 = equal weight, adjust based on your use case
# Higher weight on BM25 (0.7) = favor exact keyword matches
# Higher weight on vector (0.7) = favor semantic similarity
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5]  # Equal weighting
)

hybrid_results = ensemble_retriever.invoke(query)

print(f"\nQuery: {query}\n")
print("Hybrid (BM25 + Vector) results (top-4):")
for i, doc in enumerate(hybrid_results[:4], 1):
    print(f"{i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content}")

print("\n" + "=" * 80)
print("CASE 3: CUSTOM MANUAL HYBRID SEARCH (with detailed scoring)")
print("=" * 80)

def manual_hybrid_search(query: str, documents: list, k: int = 4, alpha: float = 0.5):
    """
    Manual hybrid search implementation showing the inner workings.
    
    Args:
        query: Search query
        documents: List of Document objects
        k: Number of results to return
        alpha: Weight for vector search (1-alpha for BM25)
               0.0 = pure BM25, 1.0 = pure vector
    """
    # 1. BM25 (keyword) scoring
    tokenized_docs = [doc.page_content.lower().split() for doc in documents]
    bm25 = BM25Okapi(tokenized_docs)
    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)
    
    # Normalize BM25 scores to [0, 1]
    bm25_scores = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min() + 1e-10)
    
    # 2. Vector (semantic) scoring
    query_embedding = embeddings.embed_query(query)
    doc_embeddings = [embeddings.embed_query(doc.page_content) for doc in documents]
    
    # Calculate cosine similarity
    vector_scores = []
    for doc_emb in doc_embeddings:
        similarity = np.dot(query_embedding, doc_emb) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb)
        )
        vector_scores.append(similarity)
    vector_scores = np.array(vector_scores)
    
    # Normalize vector scores to [0, 1]
    vector_scores = (vector_scores - vector_scores.min()) / (vector_scores.max() - vector_scores.min() + 1e-10)
    
    # 3. Combine scores
    hybrid_scores = alpha * vector_scores + (1 - alpha) * bm25_scores
    
    # 4. Get top-k
    top_indices = np.argsort(hybrid_scores)[::-1][:k]
    
    results = []
    for idx in top_indices:
        results.append({
            'document': documents[idx],
            'hybrid_score': hybrid_scores[idx],
            'vector_score': vector_scores[idx],
            'bm25_score': bm25_scores[idx]
        })
    
    return results

print(f"\nQuery: {query}\n")
print(f"Alpha (vector weight): 0.5, BM25 weight: 0.5\n")

manual_results = manual_hybrid_search(query, documents, k=4, alpha=0.5)
for i, result in enumerate(manual_results, 1):
    doc = result['document']
    print(f"{i}. [Hybrid: {result['hybrid_score']:.3f}] "
          f"[Vector: {result['vector_score']:.3f}] "
          f"[BM25: {result['bm25_score']:.3f}]")
    print(f"   [{doc.metadata.get('category', 'unknown')}] {doc.page_content}\n")

print("\n" + "=" * 80)
print("CASE 4: WEIGHTED HYBRID SEARCH (Favoring BM25 for keyword queries)")
print("=" * 80)

# When queries contain specific keywords/names, we might want to favor BM25
ensemble_retriever_bm25_heavy = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.7, 0.3]  # 70% BM25, 30% Vector - favors exact keyword matches
)

hybrid_results_bm25 = ensemble_retriever_bm25_heavy.invoke(query)

print(f"\nQuery: {query}")
print("Weights: BM25=0.7, Vector=0.3 (keyword-heavy)\n")
print("Hybrid results (BM25-weighted, top-4):")
for i, doc in enumerate(hybrid_results_bm25[:4], 1):
    print(f"{i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content}")

print("\n" + "=" * 80)
print("COMPARISON OF ALL APPROACHES")
print("=" * 80)

print("\nCase 1 - Vector-only:")
for i, doc in enumerate(vector_results, 1):
    print(f"  {i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content[:50]}...")

print("\nCase 2 - Hybrid (50/50):")
for i, doc in enumerate(hybrid_results[:4], 1):
    print(f"  {i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content[:50]}...")

print("\nCase 3 - Manual Hybrid (50/50):")
for i, result in enumerate(manual_results, 1):
    doc = result['document']
    print(f"  {i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content[:50]}...")

print("\nCase 4 - Hybrid (BM25-weighted 70/30):")
for i, doc in enumerate(hybrid_results_bm25[:4], 1):
    print(f"  {i}. [{doc.metadata.get('category', 'unknown')}] {doc.page_content[:50]}...")

print("\n" + "=" * 80)
print("KEY DIFFERENCES SUMMARY")
print("=" * 80)

summary = """
Case 1 - Vector-only Search:
  - Uses semantic similarity (cosine similarity of embeddings)
  - Good for understanding meaning and context
  - May miss exact keyword matches
  - Fast but purely semantic
  
Case 2 - Hybrid Search (EnsembleRetriever):
  - Combines BM25 (keyword matching) + Vector (semantic)
  - Uses Reciprocal Rank Fusion (RRF) to merge results
  - Balances exact keyword matching with semantic understanding
  - Best for queries that contain specific terms AND need context
  
Case 3 - Manual Hybrid (with scoring breakdown):
  - Shows how hybrid scores are calculated
  - Allows fine-grained control over scoring
  - Good for debugging and tuning
  
Case 4 - Weighted Hybrid (BM25-heavy):
  - 70% BM25 / 30% Vector weighting
  - Best when queries contain specific names, dates, or technical terms
  - Favors exact keyword matches over semantic similarity

When to use hybrid search:
  ✓ Always - it's the new baseline for RAG
  ✓ When queries contain specific terms/names (e.g., "Sarah Chen", "Q3 2024")
  ✓ When you need both semantic understanding AND exact matching
  ✓ For technical documents with domain-specific terminology
  
Weight Tuning Guidelines:
  - 0.5/0.5 (Equal): Good general-purpose balance
  - 0.7/0.3 (BM25-heavy): Use when exact keywords are critical
  - 0.3/0.7 (Vector-heavy): Use when semantic meaning is more important
  - Tune based on your specific data and query patterns

Production Recommendation:
  ┌──────────────────────────────────────────────┐
  │ Hybrid Search Pipeline                       │
  ├──────────────────────────────────────────────┤
  │ Step 1: Hybrid (BM25 + Vector)              │
  │         → Retrieve top-10 candidates         │
  │         → Use 0.5/0.5 or 0.6/0.4 weights     │
  │                                              │
  │ Step 2: (Optional) Re-rank                   │
  │         → Use cross-encoder or Cohere        │
  │         → Return top-5 final results       │
  └──────────────────────────────────────────────┘
"""

print(summary)

print("\n" + "=" * 80)
print("COMPLETE CODE EXAMPLE: Production Hybrid Search")
print("=" * 80)

complete_example = '''
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from dotenv import load_dotenv

load_dotenv()

# Your documents
docs = [Document(page_content=text, metadata={...}) for text in your_texts]

# 1. Set up embeddings and vector store
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    collection_name="your_collection",
    persist_directory="./.chromadb/your_project"
)

# 2. Create retrievers
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 10

# 3. Combine with ensemble (hybrid search)
hybrid_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5]  # Equal weights
)

# 4. Use it
results = hybrid_retriever.invoke("your search query")
# Returns: Documents ranked by combined BM25 + Vector scores
'''

print(complete_example)
