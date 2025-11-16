# Migration Guide: sentence-transformers → Azure OpenAI Embeddings

## What Changed?

We've replaced `sentence-transformers` (which downloads ~2-3GB of ML models) with **Azure OpenAI Embeddings API**. This significantly reduces your Docker image size!

## Benefits

✅ **Reduced Image Size**: From ~12.2GB to ~3-4GB (removes 2-3GB of models)  
✅ **Fits in ACR Basic Tier**: Now comfortably under 10GB limit  
✅ **Better Performance**: Azure OpenAI embeddings are optimized and fast  
✅ **No Local Models**: No need to download/store models in container  
✅ **Cost Effective**: Pay per API call instead of storing large models

## Required Changes

### 1. Update Environment Variables

Add these to your `.env` file:

```bash
# Azure OpenAI for Embeddings (REQUIRED)
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 2. Get Azure OpenAI Credentials

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your **Azure OpenAI** resource
3. Go to **"Keys and Endpoint"** section
4. Copy:
   - **Endpoint** → `AZURE_OPENAI_ENDPOINT`
   - **KEY1** or **KEY2** → `AZURE_OPENAI_API_KEY`

### 3. Deploy Embedding Model

1. In Azure Portal → Azure OpenAI resource
2. Go to **"Model deployments"**
3. Click **"Create"**
4. Select model: **text-embedding-ada-002** (or text-embedding-3-small/large)
5. Set deployment name: `text-embedding-ada-002` (or your preferred name)
6. Click **"Create"**

**Note**: Use the deployment name in `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT`

### 4. Rebuild Docker Image

```bash
# Rebuild with new dependencies
docker build -t rag-chatbot-app:latest .

# Check new size (should be much smaller!)
docker images | grep rag-chatbot
```

### 5. Update Azure Container App Environment Variables

When deploying to Azure, add these environment variables to your container app:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## Supported Models

Azure OpenAI supports these embedding models:

- **text-embedding-ada-002** (default, recommended)
- **text-embedding-3-small** (newer, smaller)
- **text-embedding-3-large** (newer, larger)

Update `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT` to match your deployment name.

## Code Changes Made

### Before (sentence-transformers):
```python
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
```

### After (Azure OpenAI):
```python
from langchain_openai import AzureOpenAIEmbeddings

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=config.azure_openai_endpoint,
    azure_deployment=config.azure_openai_deployment_name,
    api_key=config.azure_openai_api_key,
    api_version=config.azure_openai_api_version,
)
```

## Testing

1. **Test locally first**:
```bash
# Set environment variables
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-key"

# Run your application
docker compose up
```

2. **Test embeddings**:
```python
from src.core.config import get_config

config = get_config()
vectorstore = config.get_vectorstore()  # Should work with Azure OpenAI
```

## Troubleshooting

### Error: "Azure OpenAI configuration missing"

**Solution**: Make sure you've set:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`

### Error: "Deployment not found"

**Solution**: 
1. Check deployment name matches `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT`
2. Verify deployment exists in Azure Portal → Model deployments

### Error: "Invalid API key"

**Solution**:
1. Regenerate API key in Azure Portal
2. Update `AZURE_OPENAI_API_KEY` environment variable

### Error: "Rate limit exceeded"

**Solution**:
- Azure OpenAI has rate limits based on your tier
- Consider using `text-embedding-3-small` for lower costs
- Implement retry logic (already handled in code)

## Cost Considerations

### Azure OpenAI Embeddings Pricing (approximate):

- **text-embedding-ada-002**: ~$0.0001 per 1K tokens
- **text-embedding-3-small**: ~$0.00002 per 1K tokens  
- **text-embedding-3-large**: ~$0.00013 per 1K tokens

**Example**: 1M tokens/month ≈ $0.10 - $0.13/month

Much cheaper than storing 2-3GB of models in every container!

## Migration Checklist

- [ ] Created Azure OpenAI resource
- [ ] Deployed embedding model (text-embedding-ada-002)
- [ ] Got endpoint and API key
- [ ] Updated `.env` file with Azure OpenAI credentials
- [ ] Rebuilt Docker image
- [ ] Tested locally
- [ ] Updated Azure Container App environment variables
- [ ] Tested in Azure deployment

## References

- [Azure OpenAI Embeddings Tutorial](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/tutorials/embeddings)
- [Azure OpenAI Models](https://learn.microsoft.com/azure/ai-services/openai/concepts/models#embeddings-models)
- [LangChain Azure OpenAI](https://python.langchain.com/docs/integrations/platforms/azure_openai)

---

**Note**: Your existing Qdrant collections will need to be re-indexed with Azure OpenAI embeddings if you switch from sentence-transformers, as the embedding dimensions/format may differ.

