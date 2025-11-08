import os
from dotenv import load_dotenv

from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb
from agno.models.openai import OpenAIChat
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.chunking.recursive import RecursiveChunking

# Load the environment variables and configure the OpenAI API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the chat model and embedding model
chat_model = OpenAIChat(id="gpt-4.1-mini", api_key=openai_api_key)
embedding_model = OpenAIEmbedder(id="text-embedding-3-small", api_key=openai_api_key)

# Create knowledge base
knowledge = Knowledge(
    vector_db = ChromaDb(
    collection="my_documents",
    path="tmp/chromadb",
    embedder=embedding_model,
    persistent_client=True
)
)

# Add PDF file to the knowledge base
knowledge.add_content(
    path=r"E:\NLP Learning\NLP-Learning\agno-rag-agent\data\Resume_Muhammad Cikal Merdeka_AI.pdf",
    reader=PDFReader(
        chunking_strategy=RecursiveChunking()
    )
)

# Create agent with RAG
agent = Agent(
    model=chat_model,
    knowledge=knowledge,
    search_knowledge=True
)

# Run the agent
if __name__ == "__main__":
    agent.print_response(
        input="Tell me about Cikal Merdeka's work experience and skills"
)