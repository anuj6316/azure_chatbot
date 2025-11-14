#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.
set -x # Print each command before executing it.

# --- Customizable Variables ---
# Please update these variables to your desired names.
# Note: ACR_NAME and STORAGE_ACCOUNT_NAME must be globally unique.
# Use lowercase letters and numbers only for these two.
export RESOURCE_GROUP="rag-app-rg"
export LOCATION="eastus"
export ACR_NAME="ragacranujkumar" # NOTE: $RANDOM has been removed. Please choose a globally unique name.
export STORAGE_ACCOUNT_NAME="ragstorageanujkumar" # NOTE: $RANDOM has been removed. Please choose a globally unique name.
export FILE_SHARE_NAME="qdrant-storage"
export CONTAINER_APP_ENV="rag-app-env"

# --- Script ---

echo "🚀 Starting Azure deployment..."
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "ACR Name: $ACR_NAME"
echo "Storage Account: $STORAGE_ACCOUNT_NAME"

# 1. Create Resource Group
if ! az group show --name "$RESOURCE_GROUP" &>/dev/null; then
    echo "Creating resource group..."
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
else
    echo "Resource group '$RESOURCE_GROUP' already exists."
fi

# 2. Create Azure Container Registry (ACR)
if ! az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" --query "id" -o tsv &>/dev/null; then
    echo "Creating ACR..."
    az acr create --resource-group "$RESOURCE_GROUP" --name "$ACR_NAME" --sku Basic
else
    echo "ACR '$ACR_NAME' already exists."
fi
ACR_LOGIN_SERVER=$(az acr show --name "$ACR_NAME" --query loginServer -o tsv)
echo "ACR Login Server: $ACR_LOGIN_SERVER"

# Build and push images
echo "Building backend image in ACR..."
az acr build --registry "$ACR_NAME" --image rag_chatbot:latest -f dockerfile .

echo "Building frontend image in ACR..."
az acr build --registry "$ACR_NAME" --image frontend:latest -f frontend/ai-chatbot-ui/Dockerfile frontend/ai-chatbot-ui

echo "Images are ready in $ACR_LOGIN_SERVER"

# 3. Create Storage Account and File Share for Qdrant
if ! az storage account show --name "$STORAGE_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" --query "id" -o tsv &>/dev/null; then
    echo "Creating storage account..."
    az storage account create \
      --name "$STORAGE_ACCOUNT_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --location "$LOCATION" \
      --sku Standard_LRS \
      --kind StorageV2
else
    echo "Storage account '$STORAGE_ACCOUNT_NAME' already exists."
fi

STORAGE_ACCOUNT_KEY=$(az storage account keys list --account-name "$STORAGE_ACCOUNT_NAME" --query "[0].value" -o tsv)

if ! az storage share show --name "$FILE_SHARE_NAME" --account-name "$STORAGE_ACCOUNT_NAME" --account-key "$STORAGE_ACCOUNT_KEY" &>/dev/null; then
    echo "Creating file share..."
    az storage share create \
      --name "$FILE_SHARE_NAME" \
      --account-name "$STORAGE_ACCOUNT_NAME" \
      --account-key "$STORAGE_ACCOUNT_KEY"
else
    echo "File share '$FILE_SHARE_NAME' already exists."
fi
echo "Storage for Qdrant is ready."

# 4. Create Log Analytics Workspace and Container Apps Environment
export LOG_ANALYTICS_WORKSPACE="rag-app-logs-$RANDOM"

if ! az monitor log-analytics workspace show --resource-group "$RESOURCE_GROUP" --workspace-name "$LOG_ANALYTICS_WORKSPACE" &>/dev/null; then
    echo "Creating Log Analytics workspace..."
    az monitor log-analytics workspace create \
      --resource-group "$RESOURCE_GROUP" \
      --workspace-name "$LOG_ANALYTICS_WORKSPACE" \
      --location "$LOCATION"
else
    echo "Log Analytics workspace '$LOG_ANALYTICS_WORKSPACE' already exists."
fi

LOG_ANALYTICS_WORKSPACE_CLIENT_ID=$(az monitor log-analytics workspace show --query customerId -g "$RESOURCE_GROUP" -n "$LOG_ANALYTICS_WORKSPACE" -o tsv)
LOG_ANALYTICS_WORKSPACE_CLIENT_SECRET=$(az monitor log-analytics workspace get-shared-keys --query primarySharedKey -g "$RESOURCE_GROUP" -n "$LOG_ANALYTICS_WORKSPACE" -o tsv)

if ! az containerapp env show --name "$CONTAINER_APP_ENV" --resource-group "$RESOURCE_GROUP" --query "id" -o tsv &>/dev/null; then
    echo "Creating Container Apps environment..."
    az containerapp env create \
      --name "$CONTAINER_APP_ENV" \
      --resource-group "$RESOURCE_GROUP" \
      --location "$LOCATION" \
      --logs-workspace-id "$LOG_ANALYTICS_WORKSPACE_CLIENT_ID" \
      --logs-workspace-key "$LOG_ANALYTICS_WORKSPACE_CLIENT_SECRET"
else
    echo "Container Apps environment '$CONTAINER_APP_ENV' already exists."
fi

# 5. Link storage and create/update the Qdrant Container App
echo "Linking file share to Container Apps Environment..."
az containerapp env storage set \
  --name "$CONTAINER_APP_ENV" \
  --resource-group "$RESOURCE_GROUP" \
  --storage-name "qdrant-storage-link" \
  --azure-file-account-name "$STORAGE_ACCOUNT_NAME" \
  --azure-file-account-key "$STORAGE_ACCOUNT_KEY" \
  --azure-file-share-name "$FILE_SHARE_NAME" \
  --access-mode ReadWrite

if ! az containerapp show --name "qdrant-app" --resource-group "$RESOURCE_GROUP" --query "id" -o tsv &>/dev/null; then
    echo "Deploying Qdrant container..."
    az containerapp create \
      --name "qdrant-app" \
      --resource-group "$RESOURCE_GROUP" \
      --environment "$CONTAINER_APP_ENV" \
      --image "qdrant/qdrant:latest" \
      --min-replicas 1 \
      --max-replicas 1 \
      --volumes "qdrant-storage-link:/qdrant/storage" \
      --ingress internal \
      --target-port 6333
else
    echo "Container app 'qdrant-app' already exists. Updating if necessary..."
    az containerapp update \
      --name "qdrant-app" \
      --resource-group "$RESOURCE_GROUP" \
      --environment "$CONTAINER_APP_ENV" \
      --image "qdrant/qdrant:latest" \
      --min-replicas 1 \
      --max-replicas 1 \
      --volumes "qdrant-storage-link:/qdrant/storage" \
      --ingress internal \
      --target-port 6333
fi

# 6. Create/Update the Backend Container App
echo "Deploying Backend container..."
az containerapp update \
  --name "rag-backend" \
  --resource-group "$RESOURCE_GROUP" \
  --environment "$CONTAINER_APP_ENV" \
  --image "$ACR_LOGIN_SERVER/rag_chatbot:latest" \
  --registry-server "$ACR_LOGIN_SERVER" \
  --min-replicas 1 \
  --max-replicas 1 \
  --ingress internal \
  --target-port 8000 \
  --env-vars "QDRANT_URL=http://qdrant-app:6333" "APP_ENV=production"

# 7. Create/Update the Frontend Container App
echo "Deploying Frontend container..."
az containerapp update \
  --name "rag-frontend" \
  --resource-group "$RESOURCE_GROUP" \
  --environment "$CONTAINER_APP_ENV" \
  --image "$ACR_LOGIN_SERVER/frontend:latest" \
  --registry-server "$ACR_LOGIN_SERVER" \
  --min-replicas 1 \
  --max-replicas 1 \
  --ingress external \
  --target-port 80

FRONTEND_URL=$(az containerapp show --name "frontend-app" --resource-group "$RESOURCE_GROUP" --query "properties.configuration.ingress.fqdn" -o tsv)

echo "✅ Deployment successful!"
echo "Your application is available at: http://$FRONTEND_URL"

# To clean up all created resources, uncomment and run the following command:
# echo "To delete all resources, run: az group delete --name $RESOURCE_GROUP --yes"
