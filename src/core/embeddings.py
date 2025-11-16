from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from .config import get_config
from langchain_openai import AzureOpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

# Clean up any conflicting OpenAI environment variables
# These can interfere with Azure OpenAI configuration
if 'OPENAI_API_BASE' in os.environ:
    del os.environ['OPENAI_API_BASE']
if 'OPENAI_API_KEY' in os.environ and 'AZURE_OPENAI_API_KEY' in os.environ:
    # Temporarily remove generic OPENAI_API_KEY to avoid conflicts
    _original_openai_key = os.environ.pop('OPENAI_API_KEY', None)


def create_qdrant_vectorstore(
    docs,
    collection_name=None,
    qdrant_url=None,
):
    """Create a Qdrant vectorstore from documents using Azure OpenAI embeddings.
    
    Args:
        docs: List of documents to add to vectorstore
        collection_name: Name of the collection (defaults to config.qdrant_collection)
        qdrant_url: URL of Qdrant instance (defaults to config.qdrant_url)
    """
    config = get_config()
    
    if collection_name is None:
        collection_name = config.qdrant_collection
    if qdrant_url is None:
        qdrant_url = config.qdrant_url
    
    # Validate Azure OpenAI configuration
    required_env_vars = {
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
    }
    
    missing_vars = [var for var, value in required_env_vars.items() if not value]
    if missing_vars:
        raise RuntimeError(
            f"Azure OpenAI configuration missing. Please set the following environment variables:\n"
            f"{', '.join(missing_vars)}\n\n"
            f"Example .env configuration:\n"
            f"AZURE_OPENAI_API_KEY=your-api-key\n"
            f"AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/\n"
            f"AZURE_OPENAI_API_VERSION=2024-02-01\n"
            f"AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your-embedding-deployment-name"
        )

    # Initialize Azure OpenAI embeddings
    try:
        # Get Azure configuration
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
        
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment=deployment,  # This is the deployment name in Azure
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=api_version,
            # Optional: specify dimensions for text-embedding-3 models
            # dimensions=1536,
        )
        
        # Test the embeddings with a simple query
        test_embedding = embeddings.embed_query("test")
        print(f"✓ Azure OpenAI embeddings initialized successfully (dimension: {len(test_embedding)})")
        
    except Exception as e:
        raise RuntimeError(
            f"Failed to initialize Azure OpenAI embeddings. "
            f"Please verify:\n"
            f"1. AZURE_OPENAI_API_KEY is set and valid\n"
            f"2. AZURE_OPENAI_ENDPOINT is correct (format: https://your-endpoint.openai.azure.com/)\n"
            f"3. AZURE_OPENAI_EMBEDDING_DEPLOYMENT is set to your deployment name\n"
            f"4. API version is supported: {api_version}\n"
            f"5. You have access to embedding models in your Azure deployment\n"
            f"6. No conflicting OPENAI_API_BASE environment variable is set\n"
            f"Original error: {e}"
        ) from e
    
    # Create Qdrant client
    try:
        client = QdrantClient(url=qdrant_url, api_key=None, timeout=60)
        print(f"✓ Connected to Qdrant at {qdrant_url}")
    except Exception as e:
        raise RuntimeError(
            f"Failed to connect to Qdrant at {qdrant_url}. "
            f"Please verify the Qdrant instance is running.\n"
            f"Original error: {e}"
        ) from e
    
    # Check if collection exists (optional cleanup)
    try:
        collections = client.get_collections()
        if collection_name in [col.name for col in collections.collections]:
            print(f"ℹ Collection '{collection_name}' already exists. Will add to existing collection.")
        else:
            print(f"✓ Creating new collection '{collection_name}'")
    except Exception as e:
        print(f"⚠ Could not check existing collections: {e}")
    
    # Create Qdrant vectorstore from documents
    try:
        print(f"Processing {len(docs)} documents...")
        vectorstore = QdrantVectorStore.from_documents(
            documents=docs,
            embedding=embeddings,
            url=qdrant_url,
            collection_name=collection_name,
            api_key=None,
        )
        print(f"✓ Successfully created vectorstore with {len(docs)} documents")
        return vectorstore
    except Exception as e:
        raise RuntimeError(
            f"Failed to create Qdrant vectorstore. "
            f"This could be due to:\n"
            f"1. Document formatting issues\n"
            f"2. Embedding generation failures\n"
            f"3. Qdrant connection problems\n"
            f"Original error: {e}"
        ) from e


def get_existing_vectorstore(
    collection_name=None,
    qdrant_url=None,
):
    """Retrieve an existing Qdrant vectorstore.
    
    Args:
        collection_name: Name of the collection (defaults to config.qdrant_collection)
        qdrant_url: URL of Qdrant instance (defaults to config.qdrant_url)
    
    Returns:
        QdrantVectorStore: Existing vectorstore instance
    """
    config = get_config()
    
    if collection_name is None:
        collection_name = config.qdrant_collection
    if qdrant_url is None:
        qdrant_url = config.qdrant_url
    
    # Initialize embeddings (same as creation)
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
    
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=deployment,
        azure_endpoint=azure_endpoint,
        api_key=azure_api_key,
        api_version=api_version,
    )
    
    # Create Qdrant client
    client = QdrantClient(url=qdrant_url, api_key=None, timeout=60)
    
    # Return existing vectorstore
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    
    return vectorstore