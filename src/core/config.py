import os
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv

# Optional imports for vectorstore; okay if unresolved in some environments
try:
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_qdrant import Qdrant
    from qdrant_client import QdrantClient
except Exception:  # pragma: no cover
    Qdrant = None  # type: ignore
    HuggingFaceEmbeddings = None  # type: ignore
    QdrantClient = None  # type: ignore

# Load environment variables from a .env if present
load_dotenv()


class Config:
    """
    Centralized configuration for backend, vector DB, embeddings, and frontend integration.
    Values are loaded from environment variables with sensible defaults.
    """

    def __init__(self):
        # LLM / Model
        self.model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.ocr_model_name = os.getenv(
            "OCR_MODEL_NAME", "Llama-4-Maverick-17B-128E-Instruct"
        )
        self.azure_vision_endpoint = os.getenv("AZURE_VISION_ENDPOINT")
        self.azure_vision_key = os.getenv("AZURE_VISION_KEY")

        # Qdrant connection
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.qdrant_collection = os.getenv("QDRANT_COLLECTION", "rag_collection")
        self.qdrant_chat_history_collection = os.getenv(
            "QDRANT_CHAT_HISTORY_COLLECTION", "chatbot_chat_history"
        )
        # If QDRANT_URL is provided, prefer it; otherwise build from host/port
        self.qdrant_url = os.getenv("QDRANT_URL")
        if not self.qdrant_url:
            self.qdrant_url = (
                "https://qdrant-app.politewave-6298a03c.eastus.azurecontainerapps.io"
            )

        # Embeddings
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

        # Knowledge base path
        self.kb_path = Path(
            os.getenv(
                "KB_PATH",
                "data/knowledge_base",
            )
        )
        self.image_output_dir = Path(
            os.getenv(
                "IMAGE_OUTPUT_DIR",
                "output",
            )
        )

        # CORS
        # Comma-separated list, default allow all
        self.cors_allow_origins = [
            origin.strip()
            for origin in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
            if origin.strip()
        ]

        # OpenAI-compatible serving (for AI Chatbot UI)
        self.openai_compat_model_name = os.getenv(
            "OPENAI_COMPAT_MODEL", "rag-assistant"
        )
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.openai_compat_enabled = os.getenv(
            "OPENAI_COMPAT_ENABLED", "true"
        ).lower() in ("1", "true", "yes")

        # Retrieval and chunking defaults
        self.retriever_top_k = int(os.getenv("RETRIEVER_TOP_K", "10"))
        self.retriever_score_threshold = (
            float(os.getenv("RETRIEVER_SCORE_THRESHOLD"))
            if os.getenv("RETRIEVER_SCORE_THRESHOLD")
            else None
        )
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "800"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "150"))
        self.return_context = os.getenv("RETURN_CONTEXT", "true").lower() in (
            "1",
            "true",
            "yes",
        )

        # FastAPI server
        self.fastapi_host = os.getenv("FASTAPI_HOST", "0.0.0.0")
        self.fastapi_port = int(os.getenv("FASTAPI_PORT", "8000"))

        # CORS advanced
        self.cors_allow_methods = [
            m.strip()
            for m in os.getenv("CORS_ALLOW_METHODS", "*").split(",")
            if m.strip()
        ]
        self.cors_allow_headers = [
            h.strip()
            for h in os.getenv("CORS_ALLOW_HEADERS", "*").split(",")
            if h.strip()
        ]
        self.cors_allow_credentials = os.getenv(
            "CORS_ALLOW_CREDENTIALS", "true"
        ).lower() in ("1", "true", "yes")

        # Internal caches
        self._vectorstore: Optional[Any] = None

    def as_dict(self):
        return {
            "model_name": self.model_name,
            "ocr_model_name": self.ocr_model_name,
            "google_api_key": "***" if self.google_api_key else "",
            "azure_vision_endpoint": self.azure_vision_endpoint,
            "azure_vision_key": "***" if self.azure_vision_key else "",
            "qdrant_host": self.qdrant_host,
            "qdrant_port": self.qdrant_port,
            "qdrant_collection": self.qdrant_collection,
            "qdrant_url": self.qdrant_url,
            "embedding_model": self.embedding_model,
            "kb_path": str(self.kb_path),
            "image_output_dir": str(self.image_output_dir),
            "cors_allow_origins": self.cors_allow_origins,
            "openai_compat_model_name": self.openai_compat_model_name,
            "api_base_url": self.api_base_url,
            "openai_compat_enabled": self.openai_compat_enabled,
            "retriever_top_k": self.retriever_top_k,
            "retriever_score_threshold": self.retriever_score_threshold,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "return_context": self.return_context,
            "fastapi_host": self.fastapi_host,
            "fastapi_port": self.fastapi_port,
            "cors_allow_methods": self.cors_allow_methods,
            "cors_allow_headers": self.cors_allow_headers,
            "cors_allow_credentials": self.cors_allow_credentials,
        }

    def get_vectorstore(self):
        """
        Lazily initialize and cache a Qdrant vectorstore pointing at the configured collection.
        Requires Qdrant, HuggingFaceEmbeddings and qdrant_client packages to be installed.
        """
        if self._vectorstore is not None:
            return self._vectorstore
        if Qdrant is None or HuggingFaceEmbeddings is None or QdrantClient is None:
            raise RuntimeError(
                "Vectorstore dependencies are not available. Please install langchain_community, langchain_huggingface, qdrant-client."
            )
        # In get_vectorstore(), add timeout parameter
        client = QdrantClient(
            url="localhost:6333",
            api_key=None,
            timeout=60,
            # prefer_grpc=False,  # Add this
        )
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        self._vectorstore = Qdrant(
            client=client,
            collection_name=self.qdrant_collection,
            embeddings=embeddings,
        )
        return self._vectorstore


_CONFIG = None


def get_config() -> Config:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = Config()
    return _CONFIG


def get_vectorstore():
    """
    Module-level convenience accessor for the shared vectorstore.
    """
    return get_config().get_vectorstore()
