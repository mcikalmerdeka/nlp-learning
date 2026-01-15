import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_qdrant import QdrantVectorStore
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# Configuration
EMBED_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
QDRANT_URL = "http://localhost:6333"  # Docker Qdrant server
COLLECTION_NAME = "docling_demo"
TOP_K = 3

# Initialize OpenAI embeddings (same as ingest)
embedding = OpenAIEmbeddings(model=EMBED_MODEL)

# Load existing Qdrant vectorstore from Docker
print("Loading vectorstore from Docker Qdrant...")
vectorstore = QdrantVectorStore.from_existing_collection(
    embedding=embedding,
    url=QDRANT_URL,
    collection_name=COLLECTION_NAME,
)

# Initialize retriever and LLM
retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
llm = ChatOpenAI(model=LLM_MODEL, temperature=0)

# Create RAG chain using LCEL
template = """Answer the question based only on the following context:

{context}

Question: {question}

Answer:"""

prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Interactive query loop
print("✅ RAG system ready!")
print(f"🐳 Connected to Docker Qdrant at: {QDRANT_URL}")
print(f"📊 Dashboard: http://localhost:6333/dashboard\n")

while True:
    print("Question Example: What are the main AI models in Docling?")
    question = input("\n🔍 Enter your question (or 'quit' to exit): ").strip()
    
    if question.lower() in ['quit', 'exit', 'q']:
        print("Goodbye!")
        break
    
    if not question:
        continue
    
    print("\n🤔 Thinking...")
    
    # Get answer
    answer = rag_chain.invoke(question)
    
    # Display results
    print(f"\n💡 Answer:\n{answer}\n")
    
    # Get the retrieved docs to show sources
    retrieved_docs = retriever.invoke(question)
    print("📚 Sources:")
    for i, doc in enumerate(retrieved_docs):
        print(f"\n  Source {i + 1}:")
        print(f"    Text: {doc.page_content}")
        
        # Show metadata
        source = doc.metadata.get('source', 'N/A')
        print(f"    Source: {source}")
