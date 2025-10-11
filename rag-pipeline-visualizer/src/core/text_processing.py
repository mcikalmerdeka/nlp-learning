"""Text processing utilities"""

import re
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


def clean_markdown_text(text: str) -> str:
    """Clean markdown formatting and symbols from text
    
    Args:
        text: Raw text potentially containing markdown
        
    Returns:
        Cleaned text with markdown removed
    """
    # Remove markdown headers (# ## ### etc.)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    # Remove horizontal rules (--- === ***)
    text = re.sub(r'^[\-=\*]{3,}\s*$', '', text, flags=re.MULTILINE)
    
    # Remove bold/italic markers (**text** or *text* or __text__ or _text_)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # Remove inline code markers (`code`)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove image references ![alt](url)
    text = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove bullet points and list markers (-, *, •, 1., 2., etc.)
    text = re.sub(r'^[\s]*[\-\*•]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # Remove multiple consecutive blank lines (keep max 2 for paragraph separation)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace from each line
    text = '\n'.join(line.strip() for line in text.split('\n'))
    
    # Remove multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    
    return text.strip()


def chunk_text(text: str, chunk_size: int = 100, overlap: int = 20, clean_markdown: bool = True) -> List[str]:
    """Split text into overlapping chunks using RecursiveCharacterTextSplitter
    
    Args:
        text: Input text to chunk
        chunk_size: Number of words per chunk (converted to approximate characters)
        overlap: Number of overlapping words between chunks (converted to approximate characters)
        clean_markdown: Whether to clean markdown formatting before chunking (default: True)
        
    Returns:
        List of text chunks
    """
    # Clean markdown if requested
    if clean_markdown:
        text = clean_markdown_text(text)
    
    # Convert word-based sizes to character-based (avg ~5 chars per word + space)
    char_chunk_size = chunk_size * 6
    char_overlap = overlap * 6
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=char_chunk_size,
        chunk_overlap=char_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", ", ", " ", ""],
        is_separator_regex=False,
    )
    
    chunks = splitter.split_text(text)
    
    # Final cleanup: remove any empty or whitespace-only chunks
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    
    return chunks

