from pathlib import Path
from typing import Any, Dict, Tuple
from .config import get_config

from .loader import load_docs
from .splitter import split_documents
from .embeddings import create_qdrant_vectorstore

# Allow overriding KB path via env; fallback to project knowledge_base
config = get_config()
DEFAULT_KB_PATH = config.kb_path


def ingest_knowledge_base(
    base_dir: str | Path = DEFAULT_KB_PATH,
    *,
    collection_name: str = config.qdrant_collection,
    chunk_size: int = config.chunk_size,
    chunk_overlap: int = config.chunk_overlap,
    embedding_model_name: str = config.embedding_model,
    qdrant_url: str = config.qdrant_url,
) -> Tuple[Any, Dict[str, int]]:
    """Load knowledge base documents, chunk them, and upload to Qdrant."""
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
        embedding_model_name=embedding_model_name,
        qdrant_url=qdrant_url,
    )

    summary = {"documents": len(documents), "chunks": len(chunks)}
    return vectorstore, summary



if __name__ == '__main__':
    ingest_knowledge_base()
