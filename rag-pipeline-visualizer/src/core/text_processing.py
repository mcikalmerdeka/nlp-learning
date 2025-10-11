"""Text processing utilities"""

from typing import List


def chunk_text(text: str, chunk_size: int = 100, overlap: int = 20) -> List[str]:
    """Split text into overlapping chunks
    
    Args:
        text: Input text to chunk
        chunk_size: Number of words per chunk
        overlap: Number of overlapping words between chunks
        
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    
    return chunks

