```bash
├── data/
│   ├── knowledge_base/
│   ├── uploads/
│   └── vector_store/
├── frontend/
│   └── ai-chatbot-ui/
├── src/
│   ├── chatbot_backend/
│   └── core/
├── tests/
│   └── test.ipynb
├── docker-compose.yml
├── Dockerfile
└── readme.md
`
## Configuration Guide

The application uses a centralized configuration system via `src/core/config.py`. All settings have sensible defaults and can be customized through environment variables or programmatically.

### Quick Start

The configuration works out-of-the-box with defaults:

```python
from src.core.config import get_config

# Get config with all defaults
config = get_config()
print(config.as_dict())
```

### Environment Variables

Override defaults by setting environment variables in a `.env` file or system environment:

```bash
# LLM / Model Configuration
MODEL_NAME=gemini-2.0-flash
GOOGLE_API_KEY=your_api_key_here
OCR_MODEL_NAME=Llama-4-Maverick-17B-128E-Instruct

# Azure Vision (optional)
AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_VISION_KEY=your_vision_key

# Qdrant Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_URL=https://qdrant-app.politewave-6298a03c.eastus.azurecontainerapps.io
QDRANT_COLLECTION=rag_collection
QDRANT_CHAT_HISTORY_COLLECTION=chatbot_chat_history

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# File Paths
KB_PATH=data/knowledge_base
IMAGE_OUTPUT_DIR=output

# CORS Configuration
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
CORS_ALLOW_CREDENTIALS=true

# OpenAI Compatibility
OPENAI_COMPAT_ENABLED=true
OPENAI_COMPAT_MODEL=rag-assistant
API_BASE_URL=http://localhost:8000

# Retrieval Settings
RETRIEVER_TOP_K=10
RETRIEVER_SCORE_THRESHOLD=0.5

# Chunking Settings
CHUNK_SIZE=800
CHUNK_OVERLAP=150
RETURN_CONTEXT=true

# FastAPI Server
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

### Programmatic Configuration

Use setter methods to change configuration at runtime:

```python
from src.core.config import get_config

config = get_config()

# Set LLM model
config.set_model("gpt-4")

# Set Google API key
config.set_google_api_key("your_api_key")

# Configure Qdrant connection
config.set_qdrant_connection(
    host="qdrant.example.com",
    port=6333,
    url="https://qdrant.example.com"
)

# Set collection names
config.set_qdrant_collections(
    collection="my_collection",
    chat_history_collection="my_chat_history"
)

# Configure embeddings
config.set_embedding_model("sentence-transformers/all-mpnet-base-v2")

# Set file paths
config.set_paths(
    kb_path="data/my_knowledge_base",
    image_output_dir="output/images"
)

# Configure CORS
config.set_cors(
    origins=["http://localhost:3000", "https://example.com"],
    methods=["GET", "POST", "PUT", "DELETE"],
    headers=["Content-Type", "Authorization"],
    credentials=True
)

# Configure OpenAI compatibility
config.set_openai_compat(
    enabled=True,
    model_name="my-rag-model",
    api_base_url="http://localhost:8000"
)

# Set retriever parameters
config.set_retriever(top_k=20, score_threshold=0.6)

# Configure chunking
config.set_chunking(
    chunk_size=1024,
    chunk_overlap=200,
    return_context=True
)

# Configure FastAPI server
config.set_fastapi_server(host="0.0.0.0", port=8000)
```

### Default Values

| Setting | Default Value |
|---------|---------------|
| `model_name` | `gemini-2.0-flash` |
| `ocr_model_name` | `Llama-4-Maverick-17B-128E-Instruct` |
| `qdrant_host` | `localhost` |
| `qdrant_port` | `6333` |
| `qdrant_collection` | `rag_collection` |
| `qdrant_chat_history_collection` | `chatbot_chat_history` |
| `embedding_model` | `all-MiniLM-L6-v2` |
| `kb_path` | `data/knowledge_base` |
| `image_output_dir` | `output` |
| `retriever_top_k` | `10` |
| `chunk_size` | `800` |
| `chunk_overlap` | `150` |
| `fastapi_host` | `0.0.0.0` |
| `fastapi_port` | `8000` |
| `openai_compat_enabled` | `true` |
| `cors_allow_credentials` | `true` |

### Accessing Configuration

```python
from src.core.config import get_config

config = get_config()

# Access individual settings
print(config.model_name)
print(config.qdrant_host)
print(config.chunk_size)

# Get all settings as dictionary
all_settings = config.as_dict()

# Access vectorstore
vectorstore = config.get_vectorstore()
```

### Notes

- Configuration is singleton - `get_config()` always returns the same instance
- Environment variables are loaded from `.env` file if present
- All paths are converted to `Path` objects for cross-platform compatibility
- Sensitive values (API keys) are masked in `as_dict()` output
- Vectorstore is lazily initialized on first access
### Resources
- [Blog on Best OCR model for handwritten text](https://blog.roboflow.com/best-ocr-models-text-recognition/)

## Limitations Faced
- [DeepSeek OCR](https://huggingface.co/spaces/khang119966/DeepSeek-OCR-DEMO)
  - Unable to extract handwritten text
- [Qwen2.5-VL-Instruct](https://huggingface.co/spaces/mrdbourke/Qwen2.5-VL-Instruct-Demo)


## Functionality to add
[x] Session History for conversational chat
[] Ability to process mermaid code in frontend.


## Azure build
```
# In frontend/ai-chatbot-ui directory
cd ~/Downloads/rag_with_langchain/frontend/ai-chatbot-ui

# Build v6
docker build -t rag-frontend:latest .
docker tag rag-frontend:latest ragacranujkumar.azurecr.io/rag-frontend:v6
az acr login --name ragacranujkumar
docker push ragacranujkumar.azurecr.io/rag-frontend:v6
```
