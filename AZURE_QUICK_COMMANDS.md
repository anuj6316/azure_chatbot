# Azure Deployment - Quick Command Reference

Copy and paste these commands (replace placeholders with your values).

## Initial Setup

```bash
# Login to Azure
az login

# Set your variables (customize these)
RESOURCE_GROUP="rag-chatbot-rg"
ACR_NAME="ragchatbotacr"  # Must be globally unique, lowercase
LOCATION="eastus"  # or your preferred region
STORAGE_NAME="ragchatbotstorage"  # Must be globally unique, lowercase
```

## Build and Push Images

```bash
# Build your application image
docker build -t rag-chatbot-app:latest .

# Login to your ACR (replace ACR_NAME)
az acr login --name ${ACR_NAME}

# Get your ACR login server
ACR_LOGIN_SERVER=$(az acr show --name ${ACR_NAME} --query loginServer --output tsv)
echo "ACR Login Server: ${ACR_LOGIN_SERVER}"

# Tag your image
docker tag rag-chatbot-app:latest ${ACR_LOGIN_SERVER}/rag-chatbot-app:latest

# Push to ACR
docker push ${ACR_LOGIN_SERVER}/rag-chatbot-app:latest

# Verify image was pushed
az acr repository list --name ${ACR_NAME} --output table
az acr repository show-tags --name ${ACR_NAME} --repository rag-chatbot-app --output table
```

## View Logs

```bash
# View application logs
az containerapp logs show \
  --name rag-chatbot-app \
  --resource-group ${RESOURCE_GROUP} \
  --follow

# View Qdrant logs
az containerapp logs show \
  --name qdrant \
  --resource-group ${RESOURCE_GROUP} \
  --follow
```

## Get URLs

```bash
# Get application URL
az containerapp show \
  --name rag-chatbot-app \
  --resource-group ${RESOURCE_GROUP} \
  --query properties.configuration.ingress.fqdn \
  --output tsv

# Get Qdrant URL
az containerapp show \
  --name qdrant \
  --resource-group ${RESOURCE_GROUP} \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

## Update Environment Variables

```bash
# Update a single environment variable
az containerapp update \
  --name rag-chatbot-app \
  --resource-group ${RESOURCE_GROUP} \
  --set-env-vars "GOOGLE_API_KEY=your-new-key-here"

# Update multiple environment variables
az containerapp update \
  --name rag-chatbot-app \
  --resource-group ${RESOURCE_GROUP} \
  --set-env-vars \
    "QDRANT_HOST=qdrant" \
    "QDRANT_PORT=6333" \
    "MODEL_NAME=gemini-2.0-flash"
```

## Scale Containers

```bash
# Scale application to 0 (stop, save costs)
az containerapp update \
  --name rag-chatbot-app \
  --resource-group ${RESOURCE_GROUP} \
  --min-replicas 0 \
  --max-replicas 1

# Scale application back up
az containerapp update \
  --name rag-chatbot-app \
  --resource-group ${RESOURCE_GROUP} \
  --min-replicas 1 \
  --max-replicas 2
```

## Restart Containers

```bash
# Restart application
az containerapp revision restart \
  --name rag-chatbot-app \
  --resource-group ${RESOURCE_GROUP}

# Restart Qdrant
az containerapp revision restart \
  --name qdrant \
  --resource-group ${RESOURCE_GROUP}
```

## List Resources

```bash
# List all container apps
az containerapp list \
  --resource-group ${RESOURCE_GROUP} \
  --output table

# List all resources in resource group
az resource list \
  --resource-group ${RESOURCE_GROUP} \
  --output table
```

## Cleanup (Delete Everything)

```bash
# ⚠️ WARNING: This deletes ALL resources in the resource group!
az group delete \
  --name ${RESOURCE_GROUP} \
  --yes \
  --no-wait
```

## Troubleshooting Commands

```bash
# Check container app status
az containerapp show \
  --name rag-chatbot-app \
  --resource-group ${RESOURCE_GROUP} \
  --query "properties.runningStatus"

# Get recent revisions
az containerapp revision list \
  --name rag-chatbot-app \
  --resource-group ${RESOURCE_GROUP} \
  --output table

# View environment variables
az containerapp show \
  --name rag-chatbot-app \
  --resource-group ${RESOURCE_GROUP} \
  --query "properties.template.containers[0].env" \
  --output table
```

## Create Resources via CLI (Alternative to Portal)

If you prefer CLI over Portal:

```bash
# Create resource group
az group create \
  --name ${RESOURCE_GROUP} \
  --location ${LOCATION}

# Create ACR
az acr create \
  --resource-group ${RESOURCE_GROUP} \
  --name ${ACR_NAME} \
  --sku Basic \
  --admin-enabled true

# Create storage account
az storage account create \
  --resource-group ${RESOURCE_GROUP} \
  --name ${STORAGE_NAME} \
  --location ${LOCATION} \
  --sku Standard_LRS

# Create file share
az storage share create \
  --name qdrant-storage \
  --account-name ${STORAGE_NAME} \
  --quota 10

# Create Container Apps Environment
az containerapp env create \
  --name rag-chatbot-env \
  --resource-group ${RESOURCE_GROUP} \
  --location ${LOCATION}
```

---

## Environment Variables Template

Use these when creating your container app:

```bash
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=rag_collection
QDRANT_CHAT_HISTORY_COLLECTION=chatbot_chat_history
EMBEDDING_MODEL=all-MiniLM-L6-v2
MODEL_NAME=gemini-2.0-flash
GOOGLE_API_KEY=your-google-api-key-here
CORS_ALLOW_ORIGINS=*
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

