import os
from pathlib import Path
from typing import Any, Optional
import logging

from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Optional imports for vectorstore; okay if unresolved in some environments
try:
    from .embeddings import get_existing_vectorstore
except ImportError:  # pragma: no cover
    # This allows the config to be imported in environments where langchain/qdrant aren't installed
    get_existing_vectorstore = None

# Load environment variables from a .env if present
load_dotenv()


class Config:
    """
    Centralized configuration for backend, vector DB, embeddings, and frontend integration.
    All values are initialized with sensible defaults and can be overridden via environment variables or setter methods.
    """

    def __init__(self):
        # LLM / Model
        self.model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.ocr_model_name = os.getenv("OCR_MODEL_NAME", "Llama-4-Maverick-17B-128E-Instruct")
        self.azure_vision_endpoint = os.getenv("AZURE_VISION_ENDPOINT")
        self.azure_vision_key = os.getenv("AZURE_VISION_KEY")

        # Qdrant connection
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        self.qdrant_collection = os.getenv("QDRANT_COLLECTION", "rag_collection")
        self.qdrant_chat_history_collection = os.getenv("QDRANT_CHAT_HISTORY_COLLECTION", "chatbot_chat_history")
        self.qdrant_url = f"http://{self.qdrant_host}:{self.qdrant_port}"

        # SambaNova embeddings configuration
        self.sambanova_api_key = os.getenv("SAMBANOVA_API_KEY", "")
        self.sambanova_embeddings_model = os.getenv("SAMBANOVA_EMBEDDINGS_MODEL", "SambaNova-Text-Embedding-3-small")
        
        # Embeddings (legacy - kept for backward compatibility)
        self.embedding_model = os.getenv("EMBEDDING_MODEL", self.sambanova_embeddings_model)

        # Knowledge base paths
        self.kb_path = Path(os.getenv("KB_PATH", "data/knowledge_base"))
        self.image_output_dir = Path(os.getenv("IMAGE_OUTPUT_DIR", "output"))

        # CORS
        self.cors_allow_origins = self._parse_list(os.getenv("CORS_ALLOW_ORIGINS", "*"))
        self.cors_allow_methods = self._parse_list(os.getenv("CORS_ALLOW_METHODS", "*"))
        self.cors_allow_headers = self._parse_list(os.getenv("CORS_ALLOW_HEADERS", "*"))
        self.cors_allow_credentials = self._parse_bool(os.getenv("CORS_ALLOW_CREDENTIALS", "true"))

        # OpenAI-compatible serving
        self.openai_compat_model_name = os.getenv("OPENAI_COMPAT_MODEL", "rag-assistant")
        self.api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        self.openai_compat_enabled = self._parse_bool(os.getenv("OPENAI_COMPAT_ENABLED", "true"))

        # Retrieval and chunking
        self.retriever_top_k = int(os.getenv("RETRIEVER_TOP_K", "10"))
        self.retriever_score_threshold = self._parse_optional_float(os.getenv("RETRIEVER_SCORE_THRESHOLD"))
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "800"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "150"))
        self.return_context = self._parse_bool(os.getenv("RETURN_CONTEXT", "true"))

        # FastAPI server
        self.fastapi_host = os.getenv("FASTAPI_HOST", "0.0.0.0")
        self.fastapi_port = int(os.getenv("FASTAPI_PORT", "8000"))

        # Internal caches
        self._vectorstore: Optional[Any] = None

    @staticmethod
    def _parse_bool(value: str) -> bool:
        """Parse string to boolean."""
        return value.lower() in ("1", "true", "yes")

    @staticmethod
    def _parse_list(value: str) -> list[str]:
        """Parse comma-separated string to list."""
        return [item.strip() for item in value.split(",") if item.strip()]

    @staticmethod
    def _parse_optional_float(value: Optional[str]) -> Optional[float]:
        """Parse optional string to float."""
        return float(value) if value else None

    # Setter methods for easy configuration changes
    def set_model(self, model_name: str) -> None:
        """Set the LLM model name."""
        self.model_name = model_name

    def set_google_api_key(self, api_key: str) -> None:
        """Set the Google API key."""
        self.google_api_key = api_key

    def set_ocr_model(self, model_name: str) -> None:
        """Set the OCR model name."""
        self.ocr_model_name = model_name

    def set_azure_vision(self, endpoint: str, key: str) -> None:
        """Set Azure Vision endpoint and key."""
        self.azure_vision_endpoint = endpoint
        self.azure_vision_key = key

    def set_qdrant_connection(self, host: str = "localhost", port: int = 6333, url: Optional[str] = None) -> None:
        """Set Qdrant connection parameters."""
        self.qdrant_host = host
        self.qdrant_port = port
        if url:
            self.qdrant_url = url

    def set_qdrant_collections(self, collection: str, chat_history_collection: str) -> None:
        """Set Qdrant collection names."""
        self.qdrant_collection = collection
        self.qdrant_chat_history_collection = chat_history_collection

    def set_embedding_model(self, model_name: str) -> None:
        """Set the embedding model name."""
        self.embedding_model = model_name

    def set_paths(self, kb_path: str, image_output_dir: str) -> None:
        """Set knowledge base and image output paths."""
        self.kb_path = Path(kb_path)
        self.image_output_dir = Path(image_output_dir)

    def set_cors(self, origins: list[str], methods: list[str], headers: list[str], credentials: bool) -> None:
        """Set CORS configuration."""
        self.cors_allow_origins = origins
        self.cors_allow_methods = methods
        self.cors_allow_headers = headers
        self.cors_allow_credentials = credentials

    def set_openai_compat(self, enabled: bool, model_name: str = None, api_base_url: str = None) -> None:
        """Set OpenAI compatibility settings."""
        self.openai_compat_enabled = enabled
        if model_name:
            self.openai_compat_model_name = model_name
        if api_base_url:
            self.api_base_url = api_base_url

    def set_retriever(self, top_k: int = None, score_threshold: Optional[float] = None) -> None:
        """Set retriever parameters."""
        if top_k is not None:
            self.retriever_top_k = top_k
        if score_threshold is not None:
            self.retriever_score_threshold = score_threshold

    def set_chunking(self, chunk_size: int = None, chunk_overlap: int = None, return_context: bool = None) -> None:
        """Set chunking parameters."""
        if chunk_size is not None:
            self.chunk_size = chunk_size
        if chunk_overlap is not None:
            self.chunk_overlap = chunk_overlap
        if return_context is not None:
            self.return_context = return_context

    def set_fastapi_server(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Set FastAPI server configuration."""
        self.fastapi_host = host
        self.fastapi_port = port

    def as_dict(self) -> dict:
        """Return configuration as dictionary."""
        return {
            "model_name": self.model_name,
            "ocr_model_name": self.ocr_model_name,
            "google_api_key": "***" if self.google_api_key else "",
            "azure_vision_endpoint": self.azure_vision_endpoint,
            "azure_vision_key": "***" if self.azure_vision_key else "",
            "qdrant_host": self.qdrant_host,
            "qdrant_port": self.qdrant_port,
            "qdrant_collection": self.qdrant_collection,
            "qdrant_chat_history_collection": self.qdrant_chat_history_collection,
            "qdrant_url": self.qdrant_url,
            "embedding_model": self.embedding_model,
            "sambanova_api_key": "***" if self.sambanova_api_key else "",
            "sambanova_embeddings_model": self.sambanova_embeddings_model,
            "kb_path": str(self.kb_path),
            "image_output_dir": str(self.image_output_dir),
            "cors_allow_origins": self.cors_allow_origins,
            "cors_allow_methods": self.cors_allow_methods,
            "cors_allow_headers": self.cors_allow_headers,
            "cors_allow_credentials": self.cors_allow_credentials,
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
        }

    def get_vectorstore(self):
        """
        Lazily initialize and cache a Qdrant vectorstore.
        This now delegates to the centralized function in embeddings.py to ensure consistency.
        """
        if self._vectorstore is not None:
            return self._vectorstore
        if get_existing_vectorstore is None:
            raise RuntimeError(
                "Vectorstore dependencies are not available. Please install langchain_qdrant, langchain-openai, and qdrant-client."
            )
        
        # Delegate to the correct function
        self._vectorstore = get_existing_vectorstore(
            collection_name=self.qdrant_collection,
            qdrant_url=self.qdrant_url,
        )
        return self._vectorstore


_CONFIG = None


def get_config() -> Config:
    """Get or create the global config instance."""
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = Config()
    return _CONFIG


def get_vectorstore():
    """Module-level convenience accessor for the shared vectorstore."""
    return get_config().get_vectorstore()
