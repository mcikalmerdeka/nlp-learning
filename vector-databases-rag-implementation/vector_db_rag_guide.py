print("\n" + "="*70)
print("Setup complete! Choose the vector database that fits your needs.")
print("="*70)


# =============================================================================
# RETRIEVER INTERFACE - DETAILED EXPLANATION
# =============================================================================

print("\n" + "="*70)
print("RETRIEVER INTERFACE - UNIVERSAL PATTERN")
print("="*70)

"""
Understanding .as_retriever() Method
====================================

The .as_retriever() method is a LangChain standard that converts any vector 
store into a Retriever object. This provides a unified interface across all 
vector databases, making it easy to switch between them without changing 
your application code.

Key Benefits:
-------------
1. Unified Interface: Same methods (invoke, batch, stream) across all databases
2. Chain Integration: Easily use in LCEL (LangChain Expression Language) chains
3. Standard Parameters: Consistent search_type and search_kwargs across databases
4. Runnable Protocol: Inherits async support, batch processing, streaming

Basic Usage Pattern:
-------------------
"""

# Example with any vector store
def retriever_pattern_example(vectorstore):
    """Universal pattern that works with ALL vector databases"""
    
    # 1. Convert vector store to retriever
    retriever = vectorstore.as_retriever()
    
    # 2. Use invoke() to retrieve documents
    query = "What is machine learning?"
    docs = retriever.invoke(query)
    
    # 3. Process results (same format for all databases)
    for i, doc in enumerate(docs):
        print(f"Document {i+1}:")
        print(f"  Content: {doc.page_content[:100]}...")
        print(f"  Metadata: {doc.metadata}")
    
    return docs

"""
Search Types Explained:
-----------------------

1. "similarity" (default)
   - Standard semantic similarity search
   - Returns k most similar documents
   - Usage: retriever = db.as_retriever(search_type="similarity")
   
2. "mmr" (Maximum Marginal Relevance)
   - Balances similarity with diversity
   - Prevents redundant results
   - Parameters:
     * k: Number of docs to return
     * fetch_k: Number to fetch before reranking (>= k)
     * lambda_mult: 0 = max diversity, 1 = max similarity
   - Usage:
     retriever = db.as_retriever(
         search_type="mmr",
         search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5}
     )
   
3. "similarity_score_threshold"
   - Only returns docs above a similarity threshold
   - Useful for quality control
   - Parameters:
     * score_threshold: Minimum score (0.0 to 1.0)
   - Usage:
     retriever = db.as_retriever(
         search_type="similarity_score_threshold",
         search_kwargs={"score_threshold": 0.7}
     )

Common search_kwargs:
--------------------
- k: Number of documents to return (default: 4)
- fetch_k: Docs to fetch for MMR (default: 20)
- lambda_mult: MMR diversity parameter (default: 0.5)
- score_threshold: Minimum similarity score
- filter: Metadata filtering (syntax varies by database)

Database-Specific Filter Syntax:
--------------------------------
"""

# ChromaDB & pgvector - Simple dictionary
filter_chroma = {"source": "document.pdf", "category": "tech"}

# Pinecone - Nested operators
filter_pinecone = {
    "source": {"$eq": "document.pdf"},
    "page": {"$gte": 5, "$lte": 20}
}

# Qdrant - Filter objects
from qdrant_client.http import models
filter_qdrant = models.Filter(
    must=[
        models.FieldCondition(
            key="metadata.source",
            match=models.MatchValue(value="document.pdf")
        )
    ]
)

# Milvus - String expressions
filter_milvus = 'source == "document.pdf" and page >= 5'

"""
Retriever Methods:
-----------------
"""

def retriever_methods_demo(retriever):
    """All methods available on retriever objects"""
    
    query = "What is AI?"
    
    # 1. invoke() - Synchronous retrieval
    docs = retriever.invoke(query)
    
    # 2. ainvoke() - Async retrieval
    # docs = await retriever.ainvoke(query)
    
    # 3. batch() - Multiple queries at once
    queries = ["What is AI?", "What is ML?"]
    batch_results = retriever.batch(queries)
    
    # 4. abatch() - Async batch
    # batch_results = await retriever.abatch(queries)
    
    # 5. stream() - Stream results (if supported)
    # for doc in retriever.stream(query):
    #     print(doc)
    
    # 6. get_relevant_documents() - Legacy method (same as invoke)
    docs = retriever.get_relevant_documents(query)
    
    return docs

"""
Using Retrievers in RAG Chains:
-------------------------------
"""

# Example 1: Simple RAG chain with LCEL
def simple_rag_chain(retriever, llm):
    """Basic RAG pattern using LangChain Expression Language"""
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough
    
    # Define prompt template
    template = """Answer the question based only on the following context:

Context: {context}

Question: {question}

Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # Format documents helper
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Build chain using LCEL
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Use the chain
    result = chain.invoke("What is the main topic?")
    return result

# Example 2: RAG with source tracking
def rag_with_sources(retriever, llm):
    """RAG that returns sources with answer"""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough, RunnableParallel
    
    template = """Answer based on this context:
{context}

Question: {question}"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Chain that returns both answer and source documents
    chain = RunnableParallel(
        {
            "context": retriever,
            "question": RunnablePassthrough()
        }
    ).assign(
        answer=lambda x: (
            {"context": format_docs(x["context"]), "question": x["question"]}
            | prompt
            | llm
        )
    )
    
    result = chain.invoke("What is the main topic?")
    # result = {"context": [docs], "question": str, "answer": str}
    return result

# Example 3: Conversational RAG with history
def conversational_rag(retriever, llm):
    """RAG with chat history for follow-up questions"""
    from langchain.chains import create_history_aware_retriever
    from langchain_core.prompts import MessagesPlaceholder
    
    # This will reformulate questions based on chat history
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given chat history and latest question, formulate a standalone question."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])
    
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    
    # Now use history_aware_retriever in your chain
    # It will consider chat history when retrieving
    return history_aware_retriever

"""
Advanced Retriever Patterns:
----------------------------
"""

# 1. Ensemble Retriever - Combine multiple retrievers
def ensemble_retriever_example(vectorstore1, vectorstore2):
    """Combine results from multiple retrievers"""
    from langchain.retrievers import EnsembleRetriever
    
    retriever1 = vectorstore1.as_retriever(search_kwargs={"k": 3})
    retriever2 = vectorstore2.as_retriever(search_kwargs={"k": 3})
    
    # Combine with weighted results
    ensemble = EnsembleRetriever(
        retrievers=[retriever1, retriever2],
        weights=[0.5, 0.5]  # Equal weight
    )
    
    docs = ensemble.invoke("query")
    return docs

# 2. Contextual Compression - Compress retrieved docs
def compression_retriever_example(base_retriever, llm):
    """Compress documents to most relevant parts"""
    from langchain.retrievers import ContextualCompressionRetriever
    from langchain.retrievers.document_compressors import LLMChainExtractor
    
    compressor = LLMChainExtractor.from_llm(llm)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever
    )
    
    docs = compression_retriever.invoke("query")
    return docs

# 3. Multi-Query Retriever - Generate multiple queries
def multi_query_retriever_example(base_retriever, llm):
    """Generate multiple query variations for better retrieval"""
    from langchain.retrievers.multi_query import MultiQueryRetriever
    
    multi_query_retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm
    )
    
    # This generates 3-5 variations of your query automatically
    docs = multi_query_retriever.invoke("What is AI?")
    return docs

# 4. Parent Document Retriever - Retrieve larger context
def parent_document_retriever_example(vectorstore):
    """Store small chunks, retrieve larger parent documents"""
    from langchain.retrievers import ParentDocumentRetriever
    from langchain.storage import InMemoryStore
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    # Store for parent documents
    docstore = InMemoryStore()
    
    # Splitters for child and parent chunks
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
    
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=docstore,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter
    )
    
    # Add documents - it stores small chunks in vector store
    # but retrieves larger parent chunks
    # retriever.add_documents(documents)
    
    return retriever

"""
Testing Your Retriever:
----------------------
"""

def test_retriever_quality(retriever, test_queries):
    """Helper to test retriever performance"""
    
    results = {}
    
    for query in test_queries:
        docs = retriever.invoke(query)
        
        results[query] = {
            "num_results": len(docs),
            "first_result": docs[0].page_content[:100] if docs else None,
            "sources": [doc.metadata.get("source") for doc in docs]
        }
    
    return results

# Example usage
test_queries = [
    "What is the main topic?",
    "Who are the authors?",
    "What are the conclusions?"
]

# results = test_retriever_quality(retriever_chroma, test_queries)
# print(json.dumps(results, indent=2))

"""
Performance Tips:
----------------

1. Choose appropriate k value:
   - k=3-5: Most focused, fastest
   - k=10-20: Balanced
   - k=50+: Comprehensive but slower

2. Use MMR for diverse results:
   - Prevents redundant information
   - Better for exploratory queries
   - lambda_mult=0.5 is a good default

3. Set score thresholds:
   - Filters out low-quality matches
   - Prevents irrelevant context in RAG
   - Start with 0.7, adjust based on results

4. Leverage metadata filters:
   - Reduces search space
   - Faster queries
   - More relevant results

5. Batch processing:
   - Use batch() for multiple queries
   - More efficient than sequential invoke()

6. Monitor retrieval quality:
   - Log retrieved documents
   - Track relevance scores
   - A/B test different retrieval strategies
"""

print("""
Retriever Summary:
==================

✅ Use .as_retriever() to get unified interface
✅ Use .invoke(query) for synchronous retrieval
✅ Use .batch([queries]) for multiple queries
✅ Customize with search_type and search_kwargs
✅ Integrate seamlessly into LCEL chains
✅ Leverage advanced retrievers (ensemble, compression, multi-query)

Example Quick Start:
-------------------
# 1. Create retriever from any vector store
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# 2. Retrieve documents
docs = retriever.invoke("your query here")

# 3. Use in RAG chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

prompt = ChatPromptTemplate.from_template(
    "Context: {context}\\n\\nQuestion: {question}\\n\\nAnswer:"
)

def format_docs(docs):
    return "\\n\\n".join(doc.page_content for doc in docs)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = chain.invoke("What is the main topic?")
""")

print("\n" + "="*70)
print("COMPLETE RETRIEVER COMPARISON")
print("="*70)

comparison_table = """
Retriever Features by Database:
================================

┌────────────┬──────────┬──────────┬─────────────────┬──────────────────┐
│ Database   │ MMR      │ Score    │ Filter Syntax   │ Special Features │
│            │ Support  │ Threshold│                 │                  │
├────────────┼──────────┼──────────┼─────────────────┼──────────────────┤
│ ChromaDB   │    ✅    │    ✅    │ Dict (simple)   │ Easy setup       │
│ Pinecone   │    ✅    │    ✅    │ Dict (MongoDB)  │ Namespaces       │
│ Weaviate   │    ✅    │    ✅    │ Dict/Where      │ Hybrid built-in  │
│ FAISS      │    ✅    │    ✅    │ Dict+fetch_k    │ Fastest search   │
│ Qdrant     │    ✅    │    ✅    │ Filter objects  │ Advanced filters │
│ Milvus     │    ✅    │    ✅    │ String expr     │ Partitions       │
│ pgvector   │    ✅    │    ✅    │ Dict (SQL)      │ SQL integration  │
└────────────┴──────────┴──────────┴─────────────────┴──────────────────┘

Filter Syntax Examples:
======================

ChromaDB & pgvector:
-------------------
retriever = db.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {
            "source": "doc.pdf",
            "category": "tech"
        }
    }
)

Pinecone:
--------
retriever = db.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {
            "source": {"$eq": "doc.pdf"},
            "page": {"$gte": 5, "$lte": 20},
            "category": {"$in": ["tech", "science"]}
        }
    }
)

Qdrant:
------
from qdrant_client.http import models

retriever = db.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.source",
                    match=models.MatchValue(value="doc.pdf")
                )
            ],
            should=[
                models.FieldCondition(
                    key="metadata.category",
                    match=models.MatchAny(any=["tech", "science"])
                )
            ]
        )
    }
)

Milvus:
------
retriever = db.as_retriever(
    search_kwargs={
        "k": 5,
        "expr": 'source == "doc.pdf" and page >= 5 and page <= 20'
    }
)

FAISS (requires fetch_k):
------------------------
retriever = db.as_retriever(
    search_kwargs={
        "k": 5,
        "fetch_k": 20,  # Must be >= k when filtering
        "filter": {"source": "doc.pdf"}
    }
)
"""

print(comparison_table)

print("\n" + "="*70)
print("REAL-WORLD RETRIEVER EXAMPLES")
print("="*70)

"""
Example 1: Multi-Document QA System
===================================
"""

def multi_document_qa_system():
    """RAG system that searches across multiple documents"""
    
    # Setup
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    
    # Assume vectorstore is already populated with multiple docs
    # vectorstore = Chroma(...)
    
    # Create retriever that searches across all documents
    retriever = vectorstore.as_retriever(
        search_type="mmr",  # Diverse results from different docs
        search_kwargs={
            "k": 5,
            "fetch_k": 20,
            "lambda_mult": 0.5
        }
    )
    
    # Define prompt that handles multiple sources
    prompt = ChatPromptTemplate.from_template("""
Answer the question based on the following context from multiple documents.
Cite the source document for each piece of information.

Context:
{context}

Question: {question}

Answer (with sources):""")
    
    def format_docs_with_sources(docs):
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            formatted.append(f"[Source {i}: {source}]\n{doc.page_content}")
        return "\n\n".join(formatted)
    
    # Build chain
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    chain = (
        {
            "context": retriever | format_docs_with_sources,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # Use it
    answer = chain.invoke("Compare the methodologies in these papers")
    return answer

"""
Example 2: Filtered Retrieval by Date
=====================================
"""

def time_aware_retrieval(vectorstore, start_date, end_date):
    """Retrieve documents within a specific time range"""
    
    # Create retriever with date filtering
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 10,
            "filter": {
                "date": {
                    "$gte": start_date,  # Pinecone syntax
                    "$lte": end_date
                }
            }
        }
    )
    
    # For other databases, adjust filter syntax:
    # Qdrant: models.Range(gte=start_date, lte=end_date)
    # Milvus: f'date >= "{start_date}" and date <= "{end_date}"'
    
    query = "What are the latest developments?"
    recent_docs = retriever.invoke(query)
    
    return recent_docs

"""
Example 3: Category-Specific RAG
================================
"""

def category_specific_rag(vectorstore, category):
    """RAG system that only searches within a category"""
    
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    
    # Retriever filtered by category
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 5,
            "filter": {"category": category}
        }
    )
    
    prompt = ChatPromptTemplate.from_template("""
You are an expert in {category}. Answer the question using only 
information from the {category} category.

Context:
{context}

Question: {question}

Expert Answer:""")
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    llm = ChatOpenAI(temperature=0)
    
    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
            "category": lambda x: category
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

# Usage:
# tech_rag = category_specific_rag(vectorstore, "technology")
# answer = tech_rag.invoke("What are the latest trends?")

"""
Example 4: Hybrid Search with Fallback
======================================
"""

def hybrid_search_with_fallback(vectorstore):
    """Try similarity search, fallback to broader search if no results"""
    
    def smart_retriever(query: str):
        # First try: High threshold for quality results
        retriever_strict = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "score_threshold": 0.8,
                "k": 5
            }
        )
        
        docs = retriever_strict.invoke(query)
        
        # If no results, fallback to standard search
        if not docs:
            print("No high-quality matches, broadening search...")
            retriever_broad = vectorstore.as_retriever(
                search_kwargs={"k": 10}
            )
            docs = retriever_broad.invoke(query)
        
        return docs
    
    return smart_retriever

"""
Example 5: Batch Processing Multiple Queries
============================================
"""

def batch_retrieval_example(vectorstore):
    """Efficiently process multiple queries at once"""
    
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )
    
    # List of queries to process
    queries = [
        "What is machine learning?",
        "Explain neural networks",
        "What are the benefits of AI?",
        "How does deep learning work?"
    ]
    
    # Batch retrieval (more efficient than loop)
    batch_results = retriever.batch(queries)
    
    # Process results
    for query, docs in zip(queries, batch_results):
        print(f"\nQuery: {query}")
        print(f"Retrieved {len(docs)} documents")
        if docs:
            print(f"Top result: {docs[0].page_content[:100]}...")
    
    return batch_results

"""
Example 6: Async Retrieval for Better Performance
=================================================
"""

async def async_retrieval_example(vectorstore):
    """Use async for non-blocking retrieval"""
    
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 5}
    )
    
    # Single async query
    docs = await retriever.ainvoke("What is AI?")
    
    # Async batch processing
    queries = [
        "What is machine learning?",
        "Explain neural networks",
        "What are transformers?"
    ]
    
    batch_results = await retriever.abatch(queries)
    
    return batch_results

# Usage:
# import asyncio
# results = asyncio.run(async_retrieval_example(vectorstore))

"""
Example 7: Quality-Aware Retrieval
==================================
"""

def quality_aware_retrieval(vectorstore, query, min_score=0.7):
    """Only return high-quality results with scores"""
    
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "score_threshold": min_score
        }
    )
    
    docs = retriever.invoke(query)
    
    if not docs:
        return {
            "status": "no_quality_matches",
            "message": f"No documents found with score >= {min_score}",
            "documents": []
        }
    
    return {
        "status": "success",
        "num_results": len(docs),
        "documents": docs
    }

"""
Example 8: Retriever with Post-Processing
=========================================
"""

def retriever_with_postprocessing(vectorstore):
    """Add custom post-processing to retrieved documents"""
    
    base_retriever = vectorstore.as_retriever(
        search_kwargs={"k": 10}
    )
    
    def postprocess_docs(docs):
        """Custom post-processing logic"""
        
        # 1. Remove duplicates based on content similarity
        unique_docs = []
        seen_content = set()
        
        for doc in docs:
            content_hash = hash(doc.page_content[:100])
            if content_hash not in seen_content:
                unique_docs.append(doc)
                seen_content.add(content_hash)
        
        # 2. Sort by metadata (e.g., date)
        unique_docs.sort(
            key=lambda x: x.metadata.get("date", ""),
            reverse=True
        )
        
        # 3. Limit to top 5
        return unique_docs[:5]
    
    def custom_invoke(query):
        docs = base_retriever.invoke(query)
        return postprocess_docs(docs)
    
    return custom_invoke

print("""
Advanced Retriever Patterns Summary:
====================================

1. Multi-Document QA: Use MMR for diverse sources
2. Time-Aware: Filter by date ranges
3. Category-Specific: Scope search to categories
4. Hybrid with Fallback: Try strict then broad
5. Batch Processing: Handle multiple queries efficiently
6. Async Retrieval: Non-blocking for better performance
7. Quality-Aware: Enforce minimum score thresholds
8. Post-Processing: Custom logic on retrieved docs

All these patterns work with ANY vector database by using the 
unified .as_retriever() interface!
""")

print("\n" + "="*70)
print("END OF RETRIEVER GUIDE")
print("="*70)"""
Complete Vector Database RAG Guide with LangChain (2025)
=========================================================
Comprehensive examples for indexing and retrieval using 7 popular vector databases:
ChromaDB, Pinecone, Weaviate, FAISS, Qdrant, Milvus, and pgvector

This code focuses on vector database operations, not LLM frameworks.
"""

# =============================================================================
# INSTALLATION COMMANDS
# =============================================================================
"""
# Core dependencies
pip install langchain langchain-core langchain-community langchain-text-splitters
pip install langchain-openai  # or your preferred embedding provider

# Vector Database Packages
pip install langchain-chroma chromadb                    # ChromaDB
pip install langchain-pinecone pinecone                  # Pinecone
pip install langchain-weaviate weaviate-client           # Weaviate
pip install langchain-community faiss-cpu                # FAISS (or faiss-gpu)
pip install langchain-qdrant qdrant-client               # Qdrant
pip install langchain-milvus pymilvus                    # Milvus
pip install langchain-postgres psycopg[binary]           # pgvector

# Document loaders
pip install pypdf  # For PDF loading
"""

# =============================================================================
# COMMON SETUP - PDF LOADING AND TEXT SPLITTING
# =============================================================================

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import os

# Initialize embeddings (use your preferred provider)
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

def load_and_split_pdf(pdf_path: str):
    """Load PDF and split into chunks"""
    # Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    
    return chunks

# Load your PDF
# chunks = load_and_split_pdf("your_document.pdf")


# =============================================================================
# 1. CHROMADB - Local & Persistent Vector Database
# =============================================================================

from langchain_chroma import Chroma
import chromadb

print("="*70)
print("1. ChromaDB Example")
print("="*70)

# Method 1: Simple initialization with persistence
vectorstore_chroma = Chroma(
    collection_name="my_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_db"  # Data persists here
)

# Method 2: Using ChromaDB client for more control
chroma_client = chromadb.PersistentClient(path="./chroma_db")
vectorstore_chroma_client = Chroma(
    client=chroma_client,
    collection_name="my_collection",
    embedding_function=embeddings
)

# Indexing: Add documents to ChromaDB
# vectorstore_chroma.add_documents(chunks)

# Retrieval: Query ChromaDB
query = "What is the main topic of this document?"
results_chroma = vectorstore_chroma.similarity_search(
    query,
    k=3  # Return top 3 results
)

# Retrieval with scores
results_with_scores = vectorstore_chroma.similarity_search_with_score(
    query,
    k=3
)

# Filter by metadata
results_filtered = vectorstore_chroma.similarity_search(
    query,
    k=3,
    filter={"source": "specific_document.pdf"}
)

print(f"ChromaDB Query: {query}")
print(f"Results: {len(results_chroma)} documents")

# --- Using ChromaDB as a Retriever ---
print("\n--- ChromaDB as Retriever ---")

# Create retriever with default settings (similarity search, k=4)
retriever_chroma = vectorstore_chroma.as_retriever()

# Use retriever with invoke() method
retrieved_docs = retriever_chroma.invoke(query)
print(f"Retrieved {len(retrieved_docs)} documents using invoke()")

# Create retriever with custom k value
retriever_chroma_k3 = vectorstore_chroma.as_retriever(
    search_kwargs={"k": 3}
)

# Create retriever with MMR (Maximum Marginal Relevance) for diversity
retriever_chroma_mmr = vectorstore_chroma.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,  # Fetch 20 docs, then select 5 most diverse
        "lambda_mult": 0.5  # 0 = max diversity, 1 = min diversity
    }
)

# Create retriever with similarity score threshold
retriever_chroma_threshold = vectorstore_chroma.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.5  # Only return docs with score > 0.5
    }
)

# Create retriever with metadata filtering
retriever_chroma_filtered = vectorstore_chroma.as_retriever(
    search_kwargs={
        "k": 3,
        "filter": {"source": "specific_document.pdf"}
    }
)

# Using retrievers in a chain (example pattern)
# retriever_chroma.invoke() returns List[Document]
# This can be used in RAG chains like:
# chain = retriever_chroma | format_docs | llm | output_parser


# =============================================================================
# 2. PINECONE - Cloud-Native Vector Database
# =============================================================================

from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

print("\n" + "="*70)
print("2. Pinecone Example")
print("="*70)

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Create index if it doesn't exist
index_name = "langchain-rag-index"
if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=1536,  # Dimension for text-embedding-3-small
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Get the index
index = pc.Index(index_name)

# Method 1: Initialize vector store with existing index
vectorstore_pinecone = PineconeVectorStore(
    index=index,
    embedding=embeddings
)

# Method 2: From documents (indexes directly)
# vectorstore_pinecone = PineconeVectorStore.from_documents(
#     chunks,
#     embeddings,
#     index_name=index_name
# )

# Indexing: Add documents to Pinecone
# vectorstore_pinecone.add_documents(chunks)

# Retrieval: Query Pinecone
results_pinecone = vectorstore_pinecone.similarity_search(
    query,
    k=3
)

# Retrieval with scores
results_pinecone_scores = vectorstore_pinecone.similarity_search_with_score(
    query,
    k=3
)

# Filter by metadata
results_pinecone_filtered = vectorstore_pinecone.similarity_search(
    query,
    k=3,
    filter={"source": {"$eq": "specific_document.pdf"}}
)

print(f"Pinecone Query: {query}")
print(f"Results: {len(results_pinecone)} documents")

# --- Using Pinecone as a Retriever ---
print("\n--- Pinecone as Retriever ---")

# Create retriever with default settings
retriever_pinecone = vectorstore_pinecone.as_retriever()

# Use retriever with invoke() method
retrieved_docs = retriever_pinecone.invoke(query)
print(f"Retrieved {len(retrieved_docs)} documents using invoke()")

# Create retriever with custom k value
retriever_pinecone_k5 = vectorstore_pinecone.as_retriever(
    search_kwargs={"k": 5}
)

# Create retriever with MMR for diversity
retriever_pinecone_mmr = vectorstore_pinecone.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,
        "lambda_mult": 0.5
    }
)

# Create retriever with similarity score threshold
retriever_pinecone_threshold = vectorstore_pinecone.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.7
    }
)

# Create retriever with metadata filtering (Pinecone filter syntax)
retriever_pinecone_filtered = vectorstore_pinecone.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {
            "source": {"$eq": "specific_document.pdf"}
        }
    }
)

# Advanced: Namespace filtering with retriever
# retriever_pinecone_ns = vectorstore_pinecone.as_retriever(
#     search_kwargs={
#         "k": 5,
#         "namespace": "user_123"
#     }
# )


# =============================================================================
# 3. WEAVIATE - Open-Source Vector Database
# =============================================================================

from langchain_weaviate.vectorstores import WeaviateVectorStore
import weaviate

print("\n" + "="*70)
print("3. Weaviate Example")
print("="*70)

# Connect to Weaviate (local or cloud)
# For local: docker run -p 8080:8080 -p 50051:50051 semitechnologies/weaviate:latest
weaviate_client = weaviate.connect_to_local()

# Initialize vector store
vectorstore_weaviate = WeaviateVectorStore(
    client=weaviate_client,
    index_name="LangchainDocs",  # Collection name in Weaviate
    text_key="text",
    embedding=embeddings
)

# Indexing: From documents
# vectorstore_weaviate = WeaviateVectorStore.from_documents(
#     chunks,
#     embeddings,
#     client=weaviate_client,
#     index_name="LangchainDocs",
#     text_key="text"
# )

# Retrieval: Query Weaviate
results_weaviate = vectorstore_weaviate.similarity_search(
    query,
    k=3
)

# Retrieval with scores
results_weaviate_scores = vectorstore_weaviate.similarity_search_with_score(
    query,
    k=3
)

print(f"Weaviate Query: {query}")
print(f"Results: {len(results_weaviate)} documents")

# --- Using Weaviate as a Retriever ---
print("\n--- Weaviate as Retriever ---")

# Create retriever with default settings
retriever_weaviate = vectorstore_weaviate.as_retriever()

# Use retriever with invoke() method
retrieved_docs = retriever_weaviate.invoke(query)
print(f"Retrieved {len(retrieved_docs)} documents using invoke()")

# Create retriever with custom k value
retriever_weaviate_k4 = vectorstore_weaviate.as_retriever(
    search_kwargs={"k": 4}
)

# Create retriever with MMR for diversity
retriever_weaviate_mmr = vectorstore_weaviate.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,
        "lambda_mult": 0.5
    }
)

# Create retriever with similarity score threshold
retriever_weaviate_threshold = vectorstore_weaviate.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.6
    }
)

# Create retriever with metadata filtering
# Weaviate uses where filters
retriever_weaviate_filtered = vectorstore_weaviate.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"source": "specific_document.pdf"}
    }
)

# Don't forget to close the connection
weaviate_client.close()


# =============================================================================
# 4. FAISS - Fast In-Memory Vector Search
# =============================================================================

from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss

print("\n" + "="*70)
print("4. FAISS Example")
print("="*70)

# Method 1: Initialize empty FAISS index
embedding_dim = len(embeddings.embed_query("test"))
index_faiss = faiss.IndexFlatL2(embedding_dim)

vectorstore_faiss = FAISS(
    embedding_function=embeddings,
    index=index_faiss,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={}
)

# Method 2: Create from documents
# vectorstore_faiss = FAISS.from_documents(chunks, embeddings)

# Indexing: Add documents to FAISS
# vectorstore_faiss.add_documents(chunks)

# Save FAISS index to disk
# vectorstore_faiss.save_local("faiss_index")

# Load FAISS index from disk
# vectorstore_faiss = FAISS.load_local("faiss_index", embeddings)

# Retrieval: Query FAISS
results_faiss = vectorstore_faiss.similarity_search(
    query,
    k=3
)

# Retrieval with scores
results_faiss_scores = vectorstore_faiss.similarity_search_with_score(
    query,
    k=3
)

# Filter by metadata (FAISS requires fetching more then filtering)
results_faiss_filtered = vectorstore_faiss.similarity_search(
    query,
    k=3,
    filter={"source": "specific_document.pdf"},
    fetch_k=10  # Fetch 10, then filter to get 3
)

# Merge two FAISS indexes
# db1 = FAISS.from_texts(["text1"], embeddings)
# db2 = FAISS.from_texts(["text2"], embeddings)
# db1.merge_from(db2)

print(f"FAISS Query: {query}")
print(f"Results: {len(results_faiss)} documents")

# --- Using FAISS as a Retriever ---
print("\n--- FAISS as Retriever ---")

# Create retriever with default settings
retriever_faiss = vectorstore_faiss.as_retriever()

# Use retriever with invoke() method
retrieved_docs = retriever_faiss.invoke(query)
print(f"Retrieved {len(retrieved_docs)} documents using invoke()")

# Create retriever with custom k value
retriever_faiss_k5 = vectorstore_faiss.as_retriever(
    search_kwargs={"k": 5}
)

# Create retriever with MMR for diversity
retriever_faiss_mmr = vectorstore_faiss.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,  # FAISS fetches more docs then reranks
        "lambda_mult": 0.5
    }
)

# Create retriever with similarity score threshold
# Note: FAISS returns L2 distance, not similarity score
# Score threshold behavior depends on the distance metric
retriever_faiss_threshold = vectorstore_faiss.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.8
    }
)

# Create retriever with metadata filtering
# FAISS requires fetch_k > k when filtering
retriever_faiss_filtered = vectorstore_faiss.as_retriever(
    search_kwargs={
        "k": 3,
        "fetch_k": 10,  # Fetch 10, filter, return top 3
        "filter": {"source": "specific_document.pdf"}
    }
)


# =============================================================================
# 5. QDRANT - High-Performance Vector Database
# =============================================================================

from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from qdrant_client import QdrantClient
from qdrant_client.http import models

print("\n" + "="*70)
print("5. Qdrant Example")
print("="*70)

# Initialize Qdrant client
# For in-memory: QdrantClient(":memory:")
# For local: QdrantClient(path="./qdrant_db")
# For server: QdrantClient(url="http://localhost:6333")
qdrant_client = QdrantClient(":memory:")

# Create collection if needed
collection_name = "langchain_docs"
qdrant_client.create_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        size=1536,  # Dimension for text-embedding-3-small
        distance=models.Distance.COSINE
    )
)

# Method 1: Dense retrieval (standard semantic search)
vectorstore_qdrant = QdrantVectorStore(
    client=qdrant_client,
    collection_name=collection_name,
    embedding=embeddings,
    retrieval_mode=RetrievalMode.DENSE
)

# Method 2: Hybrid search (dense + sparse/BM25)
# sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
# vectorstore_qdrant_hybrid = QdrantVectorStore(
#     client=qdrant_client,
#     collection_name=collection_name,
#     embedding=embeddings,
#     sparse_embedding=sparse_embeddings,
#     retrieval_mode=RetrievalMode.HYBRID
# )

# Indexing: From documents
# vectorstore_qdrant = QdrantVectorStore.from_documents(
#     chunks,
#     embeddings,
#     location=":memory:",
#     collection_name=collection_name
# )

# Retrieval: Query Qdrant
results_qdrant = vectorstore_qdrant.similarity_search(
    query,
    k=3
)

# Retrieval with scores
results_qdrant_scores = vectorstore_qdrant.similarity_search_with_score(
    query,
    k=3
)

# Filter by metadata
results_qdrant_filtered = vectorstore_qdrant.similarity_search(
    query,
    k=3,
    filter=models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.source",
                match=models.MatchValue(value="specific_document.pdf")
            )
        ]
    )
)

print(f"Qdrant Query: {query}")
print(f"Results: {len(results_qdrant)} documents")

# --- Using Qdrant as a Retriever ---
print("\n--- Qdrant as Retriever ---")

# Create retriever with default settings
retriever_qdrant = vectorstore_qdrant.as_retriever()

# Use retriever with invoke() method
retrieved_docs = retriever_qdrant.invoke(query)
print(f"Retrieved {len(retrieved_docs)} documents using invoke()")

# Create retriever with custom k value
retriever_qdrant_k5 = vectorstore_qdrant.as_retriever(
    search_kwargs={"k": 5}
)

# Create retriever with MMR for diversity
retriever_qdrant_mmr = vectorstore_qdrant.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,
        "lambda_mult": 0.5
    }
)

# Create retriever with similarity score threshold
retriever_qdrant_threshold = vectorstore_qdrant.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.7
    }
)

# Create retriever with metadata filtering (Qdrant filter syntax)
from qdrant_client.http import models

retriever_qdrant_filtered = vectorstore_qdrant.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.source",
                    match=models.MatchValue(value="specific_document.pdf")
                )
            ]
        )
    }
)

# Advanced: Combined filters with retriever
retriever_qdrant_advanced = vectorstore_qdrant.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.category",
                    match=models.MatchValue(value="tech")
                )
            ],
            should=[
                models.FieldCondition(
                    key="metadata.priority",
                    match=models.MatchValue(value="high")
                )
            ]
        )
    }
)


# =============================================================================
# 6. MILVUS - Scalable Vector Database
# =============================================================================

from langchain_milvus import Milvus

print("\n" + "="*70)
print("6. Milvus Example")
print("="*70)

# Method 1: Milvus Lite (in-memory, for development)
URI_milvus_lite = "./milvus_demo.db"
vectorstore_milvus_lite = Milvus(
    embedding_function=embeddings,
    connection_args={"uri": URI_milvus_lite},
    collection_name="langchain_collection",
    index_params={"index_type": "FLAT", "metric_type": "L2"}
)

# Method 2: Milvus server (for production)
# URI_milvus_server = "http://localhost:19530"
# vectorstore_milvus = Milvus(
#     embedding_function=embeddings,
#     connection_args={
#         "uri": URI_milvus_server,
#         "token": "root:Milvus",
#         "db_name": "default"
#     },
#     collection_name="langchain_collection",
#     index_params={"index_type": "HNSW", "metric_type": "L2"}
# )

# Method 3: Zilliz Cloud (managed Milvus)
# vectorstore_milvus_cloud = Milvus(
#     embedding_function=embeddings,
#     connection_args={
#         "uri": "https://xxx.zillizcloud.com:443",
#         "token": "your_api_key"
#     },
#     collection_name="langchain_collection"
# )

# Indexing: Add documents
# vectorstore_milvus_lite.add_documents(chunks)

# Retrieval: Query Milvus
results_milvus = vectorstore_milvus_lite.similarity_search(
    query,
    k=3
)

# Retrieval with scores
results_milvus_scores = vectorstore_milvus_lite.similarity_search_with_score(
    query,
    k=3
)

# Filter by metadata using Milvus expression syntax
results_milvus_filtered = vectorstore_milvus_lite.similarity_search(
    query,
    k=3,
    expr='source == "specific_document.pdf"'
)

print(f"Milvus Query: {query}")
print(f"Results: {len(results_milvus)} documents")

# --- Using Milvus as a Retriever ---
print("\n--- Milvus as Retriever ---")

# Create retriever with default settings
retriever_milvus = vectorstore_milvus_lite.as_retriever()

# Use retriever with invoke() method
retrieved_docs = retriever_milvus.invoke(query)
print(f"Retrieved {len(retrieved_docs)} documents using invoke()")

# Create retriever with custom k value
retriever_milvus_k5 = vectorstore_milvus_lite.as_retriever(
    search_kwargs={"k": 5}
)

# Create retriever with MMR for diversity
retriever_milvus_mmr = vectorstore_milvus_lite.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,
        "lambda_mult": 0.5
    }
)

# Create retriever with similarity score threshold
retriever_milvus_threshold = vectorstore_milvus_lite.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.6
    }
)

# Create retriever with metadata filtering (Milvus expression syntax)
# Milvus uses string expressions for filtering
retriever_milvus_filtered = vectorstore_milvus_lite.as_retriever(
    search_kwargs={
        "k": 5,
        "expr": 'source == "specific_document.pdf"'
    }
)

# Advanced: Complex expressions with retriever
retriever_milvus_advanced = vectorstore_milvus_lite.as_retriever(
    search_kwargs={
        "k": 5,
        "expr": 'source == "document.pdf" and page > 5 and page < 20'
    }
)


# =============================================================================
# 7. PGVECTOR - PostgreSQL Vector Extension
# =============================================================================

from langchain_postgres import PGVector

print("\n" + "="*70)
print("7. pgvector (PostgreSQL) Example")
print("="*70)

# Connection string (psycopg3)
# docker run --name pgvector-container \
#   -e POSTGRES_USER=langchain \
#   -e POSTGRES_PASSWORD=langchain \
#   -e POSTGRES_DB=langchain \
#   -p 6024:5432 -d pgvector/pgvector:pg16

connection_string = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"

# Initialize pgvector store
vectorstore_pgvector = PGVector(
    embeddings=embeddings,
    collection_name="langchain_docs",
    connection=connection_string,
    use_jsonb=True  # Store metadata as JSONB for better querying
)

# Indexing: From documents
# vectorstore_pgvector = PGVector.from_documents(
#     documents=chunks,
#     embedding=embeddings,
#     collection_name="langchain_docs",
#     connection=connection_string
# )

# Retrieval: Query pgvector
results_pgvector = vectorstore_pgvector.similarity_search(
    query,
    k=3
)

# Retrieval with scores
results_pgvector_scores = vectorstore_pgvector.similarity_search_with_score(
    query,
    k=3
)

# Filter by metadata
results_pgvector_filtered = vectorstore_pgvector.similarity_search(
    query,
    k=3,
    filter={"source": "specific_document.pdf"}
)

print(f"pgvector Query: {query}")
print(f"Results: {len(results_pgvector)} documents")

# --- Using pgvector as a Retriever ---
print("\n--- pgvector as Retriever ---")

# Create retriever with default settings
retriever_pgvector = vectorstore_pgvector.as_retriever()

# Use retriever with invoke() method
retrieved_docs = retriever_pgvector.invoke(query)
print(f"Retrieved {len(retrieved_docs)} documents using invoke()")

# Create retriever with custom k value
retriever_pgvector_k5 = vectorstore_pgvector.as_retriever(
    search_kwargs={"k": 5}
)

# Create retriever with MMR for diversity
retriever_pgvector_mmr = vectorstore_pgvector.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20,
        "lambda_mult": 0.5
    }
)

# Create retriever with similarity score threshold
retriever_pgvector_threshold = vectorstore_pgvector.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.7
    }
)

# Create retriever with metadata filtering
# pgvector uses dictionary-based filtering
retriever_pgvector_filtered = vectorstore_pgvector.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"source": "specific_document.pdf"}
    }
)

# Advanced: Multiple metadata filters
retriever_pgvector_advanced = vectorstore_pgvector.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {
            "source": "document.pdf",
            "category": "tech"
        }
    }
)


# =============================================================================
# COMPARISON TABLE
# =============================================================================

print("\n" + "="*70)
print("VECTOR DATABASE COMPARISON")
print("="*70)

comparison = """
┌──────────────┬────────────┬─────────────┬──────────────┬────────────────┐
│ Database     │ Type       │ Deployment  │ Best For     │ Key Feature    │
├──────────────┼────────────┼─────────────┼──────────────┼────────────────┤
│ ChromaDB     │ Embedded   │ Local       │ Prototyping  │ Easy setup     │
│ Pinecone     │ Cloud      │ Managed     │ Production   │ Scalable       │
│ Weaviate     │ Both       │ Flexible    │ GraphQL API  │ Rich features  │
│ FAISS        │ Library    │ In-memory   │ Fast search  │ Facebook AI    │
│ Qdrant       │ Both       │ Flexible    │ Hybrid search│ Fast & robust  │
│ Milvus       │ Both       │ Flexible    │ Scale        │ Enterprise     │
│ pgvector     │ Extension  │ PostgreSQL  │ Existing DB  │ SQL native     │
└──────────────┴────────────┴─────────────┴──────────────┴────────────────┘

Performance Tips:
- ChromaDB: Great for local development, persistent storage
- Pinecone: Best for production, no infrastructure management
- Weaviate: Excellent for complex filtering and hybrid search
- FAISS: Fastest for in-memory searches, no persistence by default
- Qdrant: Strong performance with hybrid search capabilities
- Milvus: Best for large-scale deployments (millions+ vectors)
- pgvector: Perfect when you already use PostgreSQL
"""

print(comparison)


# =============================================================================
# USAGE PATTERNS FOR RAG
# =============================================================================

print("\n" + "="*70)
print("COMMON RAG USAGE PATTERN")
print("="*70)

def rag_pipeline_example(pdf_path: str, query: str, vectorstore):
    """
    Complete RAG pipeline example
    """
    # 1. Load and split PDF
    chunks = load_and_split_pdf(pdf_path)
    
    # 2. Index documents into vector store
    vectorstore.add_documents(chunks)
    print(f"Indexed {len(chunks)} chunks")
    
    # 3. Retrieve relevant documents
    retrieved_docs = vectorstore.similarity_search(query, k=3)
    
    # 4. Format context for LLM
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # 5. Create prompt (you would send this to your LLM)
    prompt = f"""Answer the question based on the context below.

Context:
{context}

Question: {query}

Answer:"""
    
    return prompt, retrieved_docs

# Example usage:
# prompt, docs = rag_pipeline_example("document.pdf", query, vectorstore_chroma)

print("""
Basic RAG Steps:
1. Load PDF with PyPDFLoader
2. Split text with RecursiveCharacterTextSplitter
3. Create embeddings with OpenAIEmbeddings (or alternatives)
4. Index into vector database with add_documents()
5. Query with similarity_search()
6. Send retrieved context + query to LLM

As Retriever for Chains:
  retriever = vectorstore.as_retriever(
      search_type="similarity",
      search_kwargs={"k": 3}
  )
""")

print("\n" + "="*70)
print("Setup complete! Choose the vector database that fits your needs.")
print("="*70)