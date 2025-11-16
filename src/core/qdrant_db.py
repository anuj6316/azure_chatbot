from pathlib import Path
from typing import Any, Dict, Tuple, Optional

from .config import get_config
from .embeddings import create_qdrant_vectorstore
from .loader import load_docs
from .splitter import split_documents


def ingest_knowledge_base(
    base_dir: Optional[str | Path] = None,
    *,
    collection_name: Optional[str] = None,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    qdrant_url: Optional[str] = None,
) -> Tuple[Any, Dict[str, int]]:
    """Load knowledge base documents, chunk them, and upload to Qdrant.
    
    Args:
        base_dir: Path to knowledge base directory (defaults to config.kb_path)
        collection_name: Qdrant collection name (defaults to config.qdrant_collection)
        chunk_size: Size of document chunks (defaults to config.chunk_size)
        chunk_overlap: Overlap between chunks (defaults to config.chunk_overlap)
        qdrant_url: URL of Qdrant instance (defaults to config.qdrant_url)
    
    Note: Embeddings are now configured via SambaNova environment variables:
        - SAMBANOVA_API_KEY
        - SAMBANOVA_EMBEDDINGS_MODEL (optional, has a default)
    """
    config = get_config()
    
    if base_dir is None:
        base_dir = config.kb_path
    if collection_name is None:
        collection_name = config.qdrant_collection
    if chunk_size is None:
        chunk_size = config.chunk_size
    if chunk_overlap is None:
        chunk_overlap = config.chunk_overlap
    if qdrant_url is None:
        qdrant_url = config.qdrant_url
    
    base_path = Path(base_dir)
    if not base_path.exists():
        raise FileNotFoundError(f"Knowledge base directory not found: {base_path}")

    documents = load_docs(str(base_path))
    if not documents:
        raise ValueError("No documents found to ingest.")

    chunks = split_documents(
        documents, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    if not chunks:
        raise ValueError("Document splitting produced no chunks. Check input data.")

    vectorstore = create_qdrant_vectorstore(
        chunks,
        collection_name=collection_name,
        qdrant_url=qdrant_url,
    )

    summary = {"documents": len(documents), "chunks": len(chunks)}
    return vectorstore, summary


if __name__ == "__main__":
    ingest_knowledge_base()
