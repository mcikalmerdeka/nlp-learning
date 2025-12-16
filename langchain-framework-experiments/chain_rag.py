import os
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Initialize model
model = init_chat_model(model="gpt-4.1-mini", api_key=os.getenv("OPENAI_API_KEY"))

# Initialize embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))

# Indexing (Load, split, store)
## 1. Load and chunk contents of the commercial lease agreement
file_paths = ["data/commercial_lease_agreement/part_1_parties_premises.pdf",
              "data/commercial_lease_agreement/part_2_rent_payment.pdf",
              "data/commercial_lease_agreement/part_3_maintenance_operations.pdf",
              "data/commercial_lease_agreement/part_4_termination_general.pdf"]
all_docs = []

for file_path in file_paths:
    loader = PyPDFLoader(file_path=file_path)
    docs = loader.load()  # All PDFs loaded as Documents
    all_docs.extend(docs)

## 2. Split the contents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
all_splits = text_splitter.split_documents(all_docs)

## 3. Store the chunks in local chroma database
vectorstore = Chroma(
    collection_name="commercial_lease_agreement",        # Name of the collection
    embedding_function=embeddings,          # Embeddings model
    persist_directory="./.chromadb/commercial_lease_agreement"  # Local folder to save data
)

# Add documents to the collection 
vectorstore.add_documents(all_splits)

# Construct a tool for retrieving context
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vectorstore.similarity_search(query, k=3)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

tools = [retrieve_context]

# Create a system prompt for the agent
system_prompt = (
    "You have access to a tool that retrieves context from a commercial lease agreement. "
    "Use the tool to help answer user queries."
)

# Create an agent with the tools and prompt
agent = create_agent(model, tools, system_prompt=system_prompt)

# Test the agent
query = "What is the termination term for this lease agreement?"

# Stream the agent's response
for step in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()