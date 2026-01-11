"""
Document processing utilities for loading, chunking, and formatting documents
"""
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import PDF_STORAGE_PATH, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP


def save_uploaded_file(uploaded_file) -> str:
    """
    Save the uploaded PDF file to storage
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        str: Path to the saved file
    """
    file_path = PDF_STORAGE_PATH + uploaded_file.name
    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    return file_path


def load_pdf_documents(file_path: str):
    """
    Load PDF documents from the uploaded file
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of loaded documents
        
    Raises:
        ValueError: If no content could be loaded from the PDF
    """
    document_loader = PyMuPDFLoader(file_path)
    docs = document_loader.load()
    if not docs:
        raise ValueError(f"Failed to load any content from PDF: {file_path}")
    return docs


def chunk_documents(raw_documents, chunk_size: int = DEFAULT_CHUNK_SIZE, 
                    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP):
    """
    Chunk the documents into smaller parts
    
    Args:
        raw_documents: List of documents to chunk
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of document chunks
        
    Raises:
        ValueError: If no documents to chunk or chunking produces no results
    """
    if not raw_documents:
        raise ValueError("No documents to chunk. The document may be empty.")
    
    text_processor = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True
    )
    chunks = text_processor.split_documents(raw_documents)
    
    if not chunks:
        raise ValueError("Chunking produced no results. The document may contain no text.")
    
    return chunks


def format_docs(docs) -> str:
    """
    Format retrieved documents into a single context string
    
    Args:
        docs: List of documents to format
        
    Returns:
        str: Formatted context string
    """
    return "\n\n".join([doc.page_content for doc in docs])
