# Azure Portal Deployment Guide - RAG Chatbot

This guide will walk you through deploying your RAG Chatbot application to Azure using the Azure Portal. We'll use **Azure Container Apps** to host your application, which is perfect for containerized applications.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Step-by-Step Deployment](#step-by-step-deployment)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [Accessing Your Application](#accessing-your-application)
6. [Troubleshooting](#troubleshooting)
7. [Cost Management](#cost-management)

---

## Prerequisites

Before starting, ensure you have:

1. ✅ **Azure Account** with an active subscription
2. ✅ **Docker Desktop** installed and running locally
3. ✅ **Azure CLI** installed (optional but helpful)
4. ✅ Your project working locally with Docker Compose
5. ✅ **Git** installed (for pushing code if needed)

---

## Architecture Overview

Your deployment will use:
- **Azure Container Registry (ACR)**: Store your Docker images
- **Azure Container Apps**: Run your containers (app + Qdrant)
- **Azure File Share**: Persistent storage for Qdrant data
- **Azure Resource Group**: Organize all resources

---

## Step-by-Step Deployment

### Step 1: Prepare Your Docker Images

First, we need to build and prepare your images for Azure.

#### 1.1 Build Your Images Locally

```bash
# Navigate to your project directory
cd /home/anuj/azure_chatbot

# Build the application image
docker build -t rag-chatbot-app:latest .

# Verify the image was created
docker images | grep rag-chatbot
```

#### 1.2 Test Locally (Optional but Recommended)

```bash
# Make sure everything works locally first
docker compose up -d

# Test the application
curl http://localhost:8000/docs

# Stop when done testing
docker compose down
```

---

### Step 2: Create Azure Resources via Portal

#### 2.1 Create Resource Group

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"** (or use the search bar)
3. Search for **"Resource group"**
4. Click **"Create"**
5. Fill in:
   - **Subscription**: Select your subscription
   - **Resource group name**: `rag-chatbot-rg` (or your preferred name)
   - **Region**: Choose closest to you (e.g., `East US`, `West Europe`)
6. Click **"Review + create"** → **"Create"**

#### 2.2 Create Azure Container Registry (ACR)

1. In the Azure Portal, click **"Create a resource"**
2. Search for **"Container Registry"**
3. Click **"Create"**
4. Fill in the form:
   - **Subscription**: Your subscription
   - **Resource group**: Select `rag-chatbot-rg` (created above)
   - **Registry name**: `ragchatbotacr` (must be globally unique, lowercase, alphanumeric)
   - **Location**: Same as resource group
   - **SKU**: **Basic** (sufficient for demo)
   - **Admin user**: **Enable** (for easier authentication)
5. Click **"Review + create"** → **"Create"**
6. Wait for deployment to complete (2-3 minutes)

**Note your ACR name** - you'll need it later!

#### 2.3 Create Storage Account for Qdrant Data

1. Click **"Create a resource"**
2. Search for **"Storage account"**
3. Click **"Create"**
4. Fill in:
   - **Subscription**: Your subscription
   - **Resource group**: `rag-chatbot-rg`
   - **Storage account name**: `ragchatbotstorage` (globally unique, lowercase)
   - **Region**: Same as resource group
   - **Performance**: **Standard**
   - **Redundancy**: **LRS** (Locally-redundant storage - cheapest for demo)
5. Click **"Review + create"** → **"Create"**
6. Wait for deployment

#### 2.4 Create File Share in Storage Account

1. Go to your newly created **Storage account**
2. In the left menu, under **"Data storage"**, click **"File shares"**
3. Click **"+ File share"**
4. Fill in:
   - **Name**: `qdrant-storage`
   - **Quota**: `10` GB (adjust as needed)
5. Click **"Create"**

---

### Step 3: Push Docker Images to ACR

#### 3.1 Login to Azure Container Registry

Open a terminal and run:

```bash
# Login to Azure (if not already logged in)
az login

# Login to your ACR (replace with your ACR name)
az acr login --name ragchatbotacr

# Get ACR login server (you'll need this)
az acr show --name ragchatbotacr --query loginServer --output tsv
```

**Note the login server URL** (e.g., `ragchatbotacr.azurecr.io`)

#### 3.2 Tag and Push Your Images

```bash
# Set your ACR name (replace with yours)
ACR_NAME="ragchatbotacr"
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"

# Tag your application image
docker tag rag-chatbot-app:latest ${ACR_LOGIN_SERVER}/rag-chatbot-app:latest

# Push the image to ACR
docker push ${ACR_LOGIN_SERVER}/rag-chatbot-app:latest

# Verify the image was pushed
az acr repository list --name ${ACR_NAME} --output table
```

**Note**: Qdrant image (`qdrant/qdrant:latest`) will be pulled directly from Docker Hub during deployment, so you don't need to push it.

---

### Step 4: Create Container Apps Environment

1. In Azure Portal, click **"Create a resource"**
2. Search for **"Container Apps"**
3. Click **"Create"**
4. Fill in the **"Basics"** tab:
   - **Subscription**: Your subscription
   - **Resource group**: `rag-chatbot-rg`
   - **Container Apps Environment name**: `rag-chatbot-env`
   - **Region**: Same as resource group
   - **Zone redundancy**: **Disabled** (for cost savings)
5. Click **"Next: Monitoring"**
6. For demo purposes, you can **disable** Application Insights (or enable if you want monitoring)
7. Click **"Review + create"** → **"Create"**
8. Wait for deployment (3-5 minutes)

---

### Step 5: Deploy Qdrant Container App

#### 5.1 Create Qdrant Container App

1. In your **Container Apps Environment**, click **"Container Apps"** in the left menu
2. Click **"+ Create"** or **"Create container app"**
3. Fill in **"Basics"**:
   - **Container app name**: `qdrant`
   - **Container Apps Environment**: Select `rag-chatbot-env`
   - **Region**: Auto-selected
4. Click **"Next: Container"**

#### 5.2 Configure Qdrant Container

1. Click **"+ Add container"**
2. Fill in:
   - **Container name**: `qdrant`
   - **Container image type**: **Public (Docker Hub or other registries)**
   - **Image and tag**: `qdrant/qdrant:latest`
   - **CPU**: `0.5` (minimum)
   - **Memory**: `1.0` Gi
3. Under **"Environment variables"**, click **"+ Add"**:
   - **Name**: `QDRANT_TELEMETRY_DISABLED`
   - **Value**: `true`
4. Click **"Next: Ingress"**

#### 5.3 Configure Ingress for Qdrant

1. **Enable ingress**: **Yes**
2. **Ingress traffic**: **Accepting traffic from anywhere**
3. **Target port**: `6333`
4. **Transport**: **HTTP**
5. Click **"Next: Networking"** → **"Next: Scale"**

#### 5.4 Configure Scaling

1. **Min replicas**: `1`
2. **Max replicas**: `1` (for demo)
3. Click **"Next: Storage"**

#### 5.5 Add Persistent Storage for Qdrant

1. Click **"+ Add storage"**
2. Fill in:
   - **Storage name**: `qdrant-storage`
   - **Storage type**: **Azure File Share**
   - **Storage account**: Select your storage account (`ragchatbotstorage`)
   - **File share**: Select `qdrant-storage`
   - **Mount path**: `/qdrant/storage`
3. Click **"Next: Tags"** → **"Review + create"** → **"Create"**
4. Wait for deployment (2-3 minutes)

**Note the Qdrant URL** from the overview page (e.g., `https://qdrant.xxxxx.azurecontainerapps.io`)

---

### Step 6: Deploy Application Container App

#### 6.1 Create Application Container App

1. In your **Container Apps Environment**, click **"Container Apps"**
2. Click **"+ Create"** or **"Create container app"**
3. Fill in **"Basics"**:
   - **Container app name**: `rag-chatbot-app`
   - **Container Apps Environment**: Select `rag-chatbot-env`
4. Click **"Next: Container"**

#### 6.2 Configure Application Container

1. Click **"+ Add container"**
2. Fill in:
   - **Container name**: `app`
   - **Container image type**: **Azure Container Registry**
   - **Registry**: Select your ACR (`ragchatbotacr`)
   - **Image and tag**: `rag-chatbot-app:latest`
   - **CPU**: `1.0`
   - **Memory**: `2.0` Gi

#### 6.3 Configure Environment Variables

Click **"+ Add"** for each environment variable:

**Qdrant Configuration:**
1. **QDRANT_HOST**: `qdrant` (service name for internal communication)
2. **QDRANT_PORT**: `6333`
3. **QDRANT_COLLECTION**: `rag_collection`
4. **QDRANT_CHAT_HISTORY_COLLECTION**: `chatbot_chat_history`

**Azure OpenAI Embeddings (REQUIRED):**
5. **AZURE_OPENAI_ENDPOINT**: `https://your-resource-name.openai.azure.com/`
6. **AZURE_OPENAI_API_KEY**: `your-azure-openai-api-key`
7. **AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT**: `text-embedding-ada-002`
8. **AZURE_OPENAI_API_VERSION**: `2024-02-15-preview`

**LLM Configuration:**
9. **MODEL_NAME**: `gemini-2.0-flash`
10. **GOOGLE_API_KEY**: `your-google-api-key-here` (if using Gemini)

**Application Configuration:**
11. **CORS_ALLOW_ORIGINS**: `*`
12. **FASTAPI_HOST**: `0.0.0.0`
13. **FASTAPI_PORT**: `8000`

**Important Notes:**
- **Azure OpenAI**: You must create an Azure OpenAI resource and deploy an embedding model first. See `AZURE_OPENAI_EMBEDDINGS_MIGRATION.md` for details.
- **Google API Key**: Only needed if you're using Gemini for LLM responses.

#### 6.4 Configure Ingress

1. **Enable ingress**: **Yes**
2. **Ingress traffic**: **Accepting traffic from anywhere**
3. **Target port**: `80` (nginx serves on port 80)
4. **Transport**: **HTTP**
5. Click **"Next: Networking"** → **"Next: Scale"**

#### 6.5 Configure Scaling

1. **Min replicas**: `1`
2. **Max replicas**: `2` (adjust as needed)
3. Click **"Next: Storage"**

#### 6.6 Add Storage (Optional - for knowledge base)

If you want persistent storage for your knowledge base:

1. Click **"+ Add storage"**
2. Fill in:
   - **Storage name**: `knowledge-base`
   - **Storage type**: **Azure File Share**
   - **Storage account**: Your storage account
   - **File share**: Create new or select existing
   - **Mount path**: `/app/data/knowledge_base`
3. Click **"Next: Tags"** → **"Review + create"** → **"Create"**
4. Wait for deployment (3-5 minutes)

---

### Step 7: Configure Networking (Internal Communication)

Since both containers are in the same Container Apps Environment, they can communicate using their service names:
- Qdrant is accessible at: `http://qdrant:6333` (internal)
- Your app should use `QDRANT_HOST=qdrant` (which we already set)

---

## Post-Deployment Configuration

### Verify Qdrant is Running

1. Go to your **Qdrant container app**
2. Check the **"Log stream"** to ensure it's running
3. Note the **Application URL** (e.g., `https://qdrant.xxxxx.azurecontainerapps.io`)
4. Test in browser: `https://qdrant.xxxxx.azurecontainerapps.io/health` (should return 404, but connection works)

### Verify Application is Running

1. Go to your **rag-chatbot-app container app**
2. Check **"Log stream"** for any errors
3. Note the **Application URL**
4. Test: `https://your-app-url.azurecontainerapps.io/docs` (should show FastAPI docs)

### Update Environment Variables if Needed

If you need to change environment variables:

1. Go to your container app
2. Click **"Revision management"** → **"Create new revision"**
3. Update environment variables
4. Create new revision

---

## Accessing Your Application

### Get Your Application URLs

1. **Qdrant Dashboard**: 
   - Go to Qdrant container app → **"Application URL"**
   - Access: `https://qdrant-url.azurecontainerapps.io/dashboard`

2. **Chatbot Application**:
   - Go to rag-chatbot-app → **"Application URL"**
   - Access: `https://your-app-url.azurecontainerapps.io`
   - API Docs: `https://your-app-url.azurecontainerapps.io/docs`

### Test Your Application

1. Open your application URL in a browser
2. You should see your chatbot frontend
3. Try sending a message to test the RAG functionality
4. Check the API docs at `/docs` endpoint

---

## Troubleshooting

### Issue: Container won't start

**Solution**:
1. Check **"Log stream"** in the container app
2. Look for error messages
3. Common issues:
   - Wrong image name/tag
   - Missing environment variables
   - Port conflicts

### Issue: Can't connect to Qdrant

**Solution**:
1. Verify `QDRANT_HOST=qdrant` is set correctly
2. Check both containers are in the same Container Apps Environment
3. Verify Qdrant container is running (check logs)

### Issue: Application shows errors

**Solution**:
1. Check container logs: **"Log stream"** or **"Logs"** tab
2. Verify all environment variables are set
3. Check if Google API key is valid (if using Gemini)

### Issue: Images not found in ACR

**Solution**:
1. Verify you pushed the image: `az acr repository list --name ragchatbotacr`
2. Check image tag matches what you specified
3. Ensure ACR admin user is enabled

### Issue: Storage mount not working

**Solution**:
1. Verify file share exists in storage account
2. Check mount path is correct (`/qdrant/storage` for Qdrant)
3. Ensure storage account and container app are in same region

---

## Cost Management

### Estimated Monthly Costs (Demo/Development)

- **Container Apps Environment**: ~$0.20/day (~$6/month)
- **Container Apps (2 apps)**: ~$0.20/day each (~$12/month)
- **ACR Basic**: ~$5/month
- **Storage Account (10GB)**: ~$0.20/month
- **Total**: ~$23-25/month

### Cost Optimization Tips

1. **Stop containers when not in use**:
   - Set **Min replicas** to `0` when not needed
   - Containers scale to zero when idle

2. **Use Basic SKU** for ACR (sufficient for demo)

3. **Delete resources when done**:
   - Delete the entire resource group to remove all resources

### Delete Resources

To avoid ongoing costs:

1. Go to your **Resource group** (`rag-chatbot-rg`)
2. Click **"Delete resource group"**
3. Type the resource group name to confirm
4. Click **"Delete"**

**Warning**: This will delete ALL resources in the group!

---

## Next Steps

1. ✅ **Custom Domain**: Add a custom domain to your container app
2. ✅ **HTTPS**: Container Apps automatically provide HTTPS
3. ✅ **Monitoring**: Enable Application Insights for better monitoring
4. ✅ **Scaling**: Adjust min/max replicas based on traffic
5. ✅ **CI/CD**: Set up GitHub Actions for automatic deployments

---

## Quick Reference Commands

```bash
# Login to Azure
az login

# Login to ACR
az acr login --name ragchatbotacr

# Push image
docker tag rag-chatbot-app:latest ragchatbotacr.azurecr.io/rag-chatbot-app:latest
docker push ragchatbotacr.azurecr.io/rag-chatbot-app:latest

# List ACR repositories
az acr repository list --name ragchatbotacr --output table

# View container app logs
az containerapp logs show --name rag-chatbot-app --resource-group rag-chatbot-rg --follow

# Delete resource group (careful!)
az group delete --name rag-chatbot-rg --yes
```

---

## Support

If you encounter issues:
1. Check Azure Container Apps [documentation](https://learn.microsoft.com/azure/container-apps/)
2. Review container logs in the Azure Portal
3. Check Azure Service Health for any outages

---

**Congratulations!** 🎉 Your RAG Chatbot is now deployed on Azure!

