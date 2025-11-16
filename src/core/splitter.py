from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from .config import get_config


def split_documents(documents, chunk_size=None, chunk_overlap=None):
    """Split documents into chunks.
    
    Args:
        documents: List of documents to split
        chunk_size: Size of each chunk (defaults to config.chunk_size)
        chunk_overlap: Overlap between chunks (defaults to config.chunk_overlap)
    """
    config = get_config()
    if chunk_size is None:
        chunk_size = config.chunk_size
    if chunk_overlap is None:
        chunk_overlap = config.chunk_overlap
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)
