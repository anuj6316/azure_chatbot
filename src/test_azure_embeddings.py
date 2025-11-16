"""
Test script for Azure OpenAI Embeddings
Run this standalone to verify your Azure configuration works
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# STEP 1: Clean up ALL conflicting variables
print("=" * 60)
print("STEP 1: Cleaning up conflicting environment variables")
print("=" * 60)

conflicting_vars = [
    'OPENAI_API_BASE', 
    'OPENAI_BASE_URL', 
    'OPENAI_API_BASE_URL',
    'OPENROUTER_API_KEY'
]

for var in conflicting_vars:
    if var in os.environ:
        print(f"⚠ Found and removing: {var} = {os.environ[var][:20]}...")
        del os.environ[var]
    else:
        print(f"✓ Not set: {var}")

print()

# STEP 2: Verify Azure configuration
print("=" * 60)
print("STEP 2: Verifying Azure OpenAI Configuration")
print("=" * 60)

required_vars = {
    "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
    "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
}

optional_vars = {
    "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
}

all_set = True
for var_name, var_value in required_vars.items():
    if var_value:
        # Mask sensitive data
        if "KEY" in var_name:
            display_value = var_value[:8] + "..." + var_value[-4:] if len(var_value) > 12 else "***"
        else:
            display_value = var_value
        print(f"✓ {var_name}: {display_value}")
    else:
        print(f"✗ {var_name}: NOT SET")
        all_set = False

for var_name, var_value in optional_vars.items():
    print(f"ℹ {var_name}: {var_value}")

if not all_set:
    print("\n❌ ERROR: Missing required environment variables!")
    print("\nYour .env file should contain:")
    print("AZURE_OPENAI_API_KEY=your-api-key")
    print("AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
    print("AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your-deployment-name")
    print("AZURE_OPENAI_API_VERSION=2024-02-01")
    exit(1)

print()

# STEP 3: Test Azure OpenAI Embeddings
print("=" * 60)
print("STEP 3: Testing Azure OpenAI Embeddings")
print("=" * 60)

try:
    from langchain_openai import AzureOpenAIEmbeddings
    
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    )
    
    print("✓ AzureOpenAIEmbeddings initialized successfully")
    
    # Test embedding generation
    print("\nTesting embedding generation...")
    test_text = "This is a test sentence for Azure OpenAI embeddings."
    embedding = embeddings.embed_query(test_text)
    
    print(f"✓ Successfully generated embedding!")
    print(f"  - Embedding dimension: {len(embedding)}")
    print(f"  - First 5 values: {embedding[:5]}")
    print(f"  - Last 5 values: {embedding[-5:]}")
    
    # Test batch embedding
    print("\nTesting batch embeddings...")
    test_docs = ["Document 1", "Document 2", "Document 3"]
    batch_embeddings = embeddings.embed_documents(test_docs)
    print(f"✓ Successfully generated {len(batch_embeddings)} embeddings")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED! Your Azure OpenAI setup is working correctly.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: Failed to initialize or test embeddings")
    print(f"\nError details: {e}")
    print(f"\nError type: {type(e).__name__}")
    
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING TIPS:")
    print("=" * 60)
    print("1. Verify your deployment name in Azure Portal")
    print("2. Check that your endpoint URL is correct (no trailing slash)")
    print("3. Ensure API key has proper permissions")
    print("4. Confirm API version is supported by your deployment")
    print("5. Make sure no other code is setting OPENAI_API_BASE")
    exit(1)