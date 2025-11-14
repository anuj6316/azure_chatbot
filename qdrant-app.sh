#!/bin/bash

# ---------------------------
# CONFIGURATION
# ---------------------------
RESOURCE_GROUP="docker_RG"
ACI_NAME="rag-backend"
ACR_NAME="ragacranujkumar"
IMAGE_NAME="rag_chatbot:latest"
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"

echo "🚀 Starting deployment..."

# ---------------------------
# 1. Build Docker image locally (very fast thanks to cache)
# ---------------------------
echo "🐳 Building Docker image locally..."
docker build -t ${ACR_LOGIN_SERVER}/${IMAGE_NAME} .

if [ $? -ne 0 ]; then
  echo "❌ Docker build failed. Exiting."
  exit 1
fi

# ---------------------------
# 2. Login to ACR
# ---------------------------
echo "🔐 Logging in to Azure Container Registry..."
az acr login --name ${ACR_NAME}

if [ $? -ne 0 ]; then
  echo "❌ ACR login failed. Exiting."
  exit 1
fi

# ---------------------------
# 3. Push the image
# ---------------------------
echo "📤 Pushing image to ACR..."
docker push ${ACR_LOGIN_SERVER}/${IMAGE_NAME}

if [ $? -ne 0 ]; then
  echo "❌ Docker push failed. Exiting."
  exit 1
fi

# ---------------------------
# 4. Restart Container Instance
# ---------------------------
echo "🔄 Restarting Azure Container Instance..."
az container restart \
  --name ${ACI_NAME} \
  --resource-group ${RESOURCE_GROUP}

if [ $? -ne 0 ]; then
  echo "⚠️ Restart failed. You may need to delete and recreate the container manually."
else
  echo "✅ ACI restarted successfully!"
fi

echo "🎉 Deployment completed successfully!"
