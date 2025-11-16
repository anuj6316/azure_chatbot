# Azure Deployment Checklist

Use this checklist to track your deployment progress.

## Pre-Deployment

- [ ] Azure account created and subscription active
- [ ] Docker Desktop installed and running
- [ ] Azure CLI installed (`az --version` works)
- [ ] Project tested locally with `docker compose up`
- [ ] All environment variables documented
- [ ] Google API key ready (if using Gemini)

## Step 1: Build Images

- [ ] Built application image: `docker build -t rag-chatbot-app:latest .`
- [ ] Verified image exists: `docker images | grep rag-chatbot`
- [ ] Tested locally (optional but recommended)

## Step 2: Azure Portal Setup

- [ ] Created Resource Group: `rag-chatbot-rg`
- [ ] Created Azure Container Registry (ACR): `ragchatbotacr`
  - [ ] Admin user enabled
  - [ ] Noted ACR login server URL
- [ ] Created Storage Account: `ragchatbotstorage`
- [ ] Created File Share: `qdrant-storage` (10GB)

## Step 3: Push Images

- [ ] Logged in to Azure: `az login`
- [ ] Logged in to ACR: `az acr login --name ragchatbotacr`
- [ ] Tagged image: `docker tag rag-chatbot-app:latest <acr>.azurecr.io/rag-chatbot-app:latest`
- [ ] Pushed image: `docker push <acr>.azurecr.io/rag-chatbot-app:latest`
- [ ] Verified image in ACR: `az acr repository list --name ragchatbotacr`

## Step 4: Container Apps Environment

- [ ] Created Container Apps Environment: `rag-chatbot-env`
- [ ] Environment deployment completed

## Step 5: Deploy Qdrant

- [ ] Created Qdrant container app: `qdrant`
- [ ] Configured container:
  - [ ] Image: `qdrant/qdrant:latest`
  - [ ] CPU: 0.5, Memory: 1.0 Gi
  - [ ] Environment variable: `QDRANT_TELEMETRY_DISABLED=true`
- [ ] Configured ingress:
  - [ ] Enabled ingress
  - [ ] Target port: 6333
- [ ] Added storage:
  - [ ] Storage name: `qdrant-storage`
  - [ ] Mount path: `/qdrant/storage`
- [ ] Qdrant deployment completed
- [ ] Noted Qdrant URL

## Step 6: Deploy Application

- [ ] Created application container app: `rag-chatbot-app`
- [ ] Configured container:
  - [ ] Image from ACR: `rag-chatbot-app:latest`
  - [ ] CPU: 1.0, Memory: 2.0 Gi
- [ ] Set environment variables:
  - [ ] `QDRANT_HOST=qdrant`
  - [ ] `QDRANT_PORT=6333`
  - [ ] `QDRANT_COLLECTION=rag_collection`
  - [ ] `QDRANT_CHAT_HISTORY_COLLECTION=chatbot_chat_history`
  - [ ] `EMBEDDING_MODEL=all-MiniLM-L6-v2`
  - [ ] `MODEL_NAME=gemini-2.0-flash`
  - [ ] `GOOGLE_API_KEY=<your-key>` (if applicable)
  - [ ] `CORS_ALLOW_ORIGINS=*`
  - [ ] `FASTAPI_HOST=0.0.0.0`
  - [ ] `FASTAPI_PORT=8000`
- [ ] Configured ingress:
  - [ ] Enabled ingress
  - [ ] Target port: 80
- [ ] Application deployment completed
- [ ] Noted Application URL

## Step 7: Verification

- [ ] Qdrant container running (checked logs)
- [ ] Application container running (checked logs)
- [ ] Tested Qdrant URL (if accessible)
- [ ] Tested Application URL: `https://<app-url>/docs`
- [ ] Tested chatbot functionality
- [ ] Verified API endpoints working

## Post-Deployment

- [ ] Saved all URLs:
  - [ ] Qdrant URL: `___________________________`
  - [ ] Application URL: `___________________________`
  - [ ] API Docs URL: `___________________________`
- [ ] Documented any custom configurations
- [ ] Set up monitoring (optional)
- [ ] Configured cost alerts (optional)

## Cleanup (When Done)

- [ ] Stopped containers (set min replicas to 0) OR
- [ ] Deleted resource group to avoid costs

---

## Quick Notes

**Resource Names Used:**
- Resource Group: `rag-chatbot-rg`
- ACR: `ragchatbotacr`
- Storage: `ragchatbotstorage`
- Environment: `rag-chatbot-env`
- Qdrant App: `qdrant`
- App Container: `rag-chatbot-app`

**Important URLs:**
- ACR Login Server: `___________________________`
- Qdrant URL: `___________________________`
- Application URL: `___________________________`

**Cost Estimate:** ~$23-25/month (can be reduced by scaling to zero when not in use)

