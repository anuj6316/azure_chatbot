# Configuration System Updates

## Overview
The configuration system has been refactored to be simpler, more maintainable, and follow Python best practices. All config-related code across the project has been updated to work with the new simplified config system.

## Key Changes

### 1. **src/core/config.py** - Simplified Configuration Class
- **Before**: Complex initialization with many inline environment variable checks
- **After**: Clean initialization with sensible defaults and helper methods
- **New Features**:
  - Added `_parse_bool()`, `_parse_list()`, `_parse_optional_float()` helper methods
  - Added setter methods for easy runtime configuration changes:
    - `set_model()`, `set_google_api_key()`, `set_ocr_model()`
    - `set_azure_vision()`, `set_qdrant_connection()`, `set_qdrant_collections()`
    - `set_embedding_model()`, `set_paths()`, `set_cors()`
    - `set_openai_compat()`, `set_retriever()`, `set_chunking()`, `set_fastapi_server()`

### 2. **src/core/retriver.py** - Fixed Default Parameter Issue
- **Before**: Used `config.retriever_top_k` as default parameter (evaluated at import time)
- **After**: Uses `None` as default and calls `get_config()` inside function
- **Benefit**: Config changes are reflected at runtime

### 3. **src/core/splitter.py** - Fixed Default Parameter Issue
- **Before**: Used `config.chunk_size` and `config.chunk_overlap` as default parameters
- **After**: Uses `None` as defaults and resolves from config inside function
- **Benefit**: Allows runtime configuration changes

### 4. **src/core/embeddings.py** - Fixed Default Parameter Issue
- **Before**: Used config values as default parameters
- **After**: Uses `None` as defaults and resolves from config inside function
- **Added**: Comprehensive docstring explaining parameters

### 5. **src/core/qdrant_db.py** - Fixed Default Parameter Issue
- **Before**: Used config values as default parameters at module level
- **After**: Uses `None` as defaults and resolves from config inside function
- **Benefit**: More flexible and testable

### 6. **src/core/loader.py** - Fixed Config Usage
- **Before**: Created `config` instance at module level and used it globally
- **After**: Calls `get_config()` inside functions where needed
- **Fixed**: `IMAGE_OUTPUT_DIR` initialization moved inside `_load_handwritten_notes()`
- **Fixed**: `load_docs()` function now accepts optional `base_dir` parameter

### 7. **src/core/chat_manager.py** - Removed Global Config
- **Before**: Created `config` instance at module level
- **After**: Removed global config, calls `get_config()` inside functions
- **Fixed**: `get_llm()` function now accepts optional `model_name` parameter

### 8. **src/chatbot_backend/rag_api.py** - Improved Config Usage
- **Before**: Created config at module level before app initialization
- **After**: Creates config after app initialization with clear comment
- **Benefit**: Better code organization and clarity

## Best Practices Applied

1. **Lazy Initialization**: Config values are resolved at function call time, not import time
2. **Singleton Pattern**: `get_config()` always returns the same instance
3. **Optional Parameters**: Functions use `None` as default and resolve from config inside
4. **Docstrings**: All functions have clear docstrings explaining parameters
5. **Type Hints**: Proper type hints for all parameters and return values
6. **Error Handling**: Better error messages and validation

## Migration Guide

### For Existing Code
If you have code using the old config pattern:

```python
# OLD (Don't use)
from .config import get_config
config = get_config()
def my_function(param=config.some_value):
    pass
```

Use the new pattern:

```python
# NEW (Use this)
from .config import get_config
def my_function(param=None):
    if param is None:
        param = get_config().some_value
    # ... rest of function
```

### For Runtime Configuration Changes
You can now easily change configuration at runtime:

```python
from src.core.config import get_config

config = get_config()

# Change settings
config.set_model("gpt-4")
config.set_chunking(chunk_size=1024, chunk_overlap=200)
config.set_qdrant_connection(host="new-host.com", port=6333)

# All subsequent calls will use the new configuration
```

## Testing
All changes maintain backward compatibility with existing code while providing better flexibility for testing and runtime configuration changes.

## Files Modified
1. `/home/anuj/azure_chatbot/src/core/config.py`
2. `/home/anuj/azure_chatbot/src/core/retriver.py`
3. `/home/anuj/azure_chatbot/src/core/splitter.py`
4. `/home/anuj/azure_chatbot/src/core/embeddings.py`
5. `/home/anuj/azure_chatbot/src/core/qdrant_db.py`
6. `/home/anuj/azure_chatbot/src/core/loader.py`
7. `/home/anuj/azure_chatbot/src/core/chat_manager.py`
8. `/home/anuj/azure_chatbot/src/chatbot_backend/rag_api.py`
