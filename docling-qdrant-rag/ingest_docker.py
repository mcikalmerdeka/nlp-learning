import os
from dotenv import load_dotenv
from langchain_docling.loader import DoclingLoader, ExportType
from docling.chunking import HybridChunker
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

# https://github.com/huggingface/transformers/issues/5486:
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load environment variables
load_dotenv()

# Configuration
FILE_PATH = ["https://arxiv.org/pdf/2408.09869"]  # Docling Technical Report
EMBED_MODEL = "text-embedding-3-small"  # OpenAI embedding model
EXPORT_TYPE = ExportType.DOC_CHUNKS
QDRANT_URL = "http://localhost:6333"  # Docker Qdrant server
COLLECTION_NAME = "docling_demo"

print("Loading documents with Docling...")
loader = DoclingLoader(
    file_path=FILE_PATH,
    export_type=EXPORT_TYPE,
    chunker=HybridChunker(tokenizer="sentence-transformers/all-MiniLM-L6-v2"),
)

docs = loader.load()
print(f"Loaded {len(docs)} document chunks")

# Determine splits
if EXPORT_TYPE == ExportType.DOC_CHUNKS:
    splits = docs
elif EXPORT_TYPE == ExportType.MARKDOWN:
    from langchain_text_splitters import MarkdownHeaderTextSplitter

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "Header_1"),
            ("##", "Header_2"),
            ("###", "Header_3"),
        ],
    )
    splits = [split for doc in docs for split in splitter.split_text(doc.page_content)]
else:
    raise ValueError(f"Unexpected export type: {EXPORT_TYPE}")

# Sample splits
print("\nSample splits:")
for d in splits[:3]:
    print(f"- {d.page_content[:100]}...")
print("...")

# Initialize OpenAI embeddings
print("\nInitializing OpenAI embeddings...")
embedding = OpenAIEmbeddings(model=EMBED_MODEL)

# Create Qdrant vectorstore connected to Docker
print("Creating Qdrant vectorstore (connecting to Docker)...")
vectorstore = QdrantVectorStore.from_documents(
    documents=splits,
    embedding=embedding,
    url=QDRANT_URL,
    collection_name=COLLECTION_NAME,
)

print(f"\n✅ Successfully created vectorstore with {len(splits)} chunks!")
print(f"🐳 Connected to Docker Qdrant at: {QDRANT_URL}")
print(f"📊 Dashboard available at: http://localhost:6333/dashboard")
