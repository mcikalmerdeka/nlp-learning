"""
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