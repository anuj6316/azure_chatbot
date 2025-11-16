# Fixes Applied to Configuration and Vectorstore

## Issues Fixed

### 1. **LangChain Deprecation Warning**
**Problem**: 
```
LangChainDeprecationWarning: The class `Qdrant` was deprecated in LangChain 0.1.2 and will be removed in 0.5.0. Use :class`~QdrantVectorStore` instead.
```

**Solution**:
- Updated imports in `config.py` from `langchain_qdrant.Qdrant` to `langchain_qdrant.QdrantVectorStore`
- Updated `embeddings.py` to use `QdrantVectorStore` instead of deprecated `Qdrant`
- Updated `get_vectorstore()` method to use `QdrantVectorStore` with correct parameters

### 2. **Qdrant Collection 404 Error**
**Problem**:
```
POST /collections/rag_collection/points/search HTTP/1.1" 404 106
```

**Root Causes**:
- Hardcoded localhost URL in `get_vectorstore()` instead of using configured `qdrant_url`
- Incorrect client initialization parameters
- Collection might not exist or be accessible

**Solution**:
- Updated `get_vectorstore()` to use `self.qdrant_url` from config instead of hardcoded "localhost:6333"
- Fixed QdrantClient initialization to use the configured URL
- Updated error handling in `create_qdrant_vectorstore()` to gracefully handle missing collections

## Files Modified

### 1. **src/core/config.py**
Changes:
- Updated import: `from langchain_qdrant import QdrantVectorStore` (instead of `Qdrant`)
- Fixed `get_vectorstore()` method:
  - Now uses `self.qdrant_url` instead of hardcoded "localhost:6333"
  - Uses `QdrantVectorStore` instead of deprecated `Qdrant`
  - Passes `embedding` parameter instead of `embeddings`
  - Updated error message to reference correct packages

### 2. **src/core/embeddings.py**
Changes:
- Updated import: `from langchain_qdrant import QdrantVectorStore`
- Updated `create_qdrant_vectorstore()`:
  - Uses `QdrantVectorStore.from_documents()` instead of `Qdrant.from_documents()`
  - Creates QdrantClient with `url=qdrant_url` parameter
  - Added try-except for collection deletion to handle non-existent collections gracefully
  - Passes correct parameters to `QdrantVectorStore.from_documents()`

## Configuration Parameters

The following environment variables control Qdrant connection:

```bash
# Qdrant Connection
QDRANT_HOST=localhost              # Host (used for local connections)
QDRANT_PORT=6333                   # Port (used for local connections)
QDRANT_URL=https://...             # Full URL (takes precedence)
QDRANT_COLLECTION=rag_collection   # Collection name
```

## Testing the Fix

To verify the fixes work:

1. **Check for deprecation warnings**: The warning should no longer appear
2. **Check for 404 errors**: The collection should be found if it exists
3. **Verify connection**: Ensure `QDRANT_URL` environment variable is set correctly

Example `.env` file:
```bash
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=rag_collection
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## API Changes

### Before
```python
from langchain_qdrant import Qdrant
vectorstore = Qdrant(
    client=client,
    collection_name=collection_name,
    embeddings=embeddings,  # Wrong parameter name
)
```

### After
```python
from langchain_qdrant import QdrantVectorStore
vectorstore = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings,  # Correct parameter name
)
```

## Backward Compatibility

These changes maintain backward compatibility with existing code while fixing the deprecation warnings and connection issues. All function signatures remain the same.

## Next Steps

1. Ensure Qdrant server is running and accessible at the configured URL
2. Verify the collection exists or will be created during ingestion
3. Test the chat endpoint to confirm vectorstore queries work correctly
