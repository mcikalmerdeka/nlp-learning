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
print("="*70)