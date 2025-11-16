# Azure Image Size Solution

## Problem
Your Docker image is **12.7GB**, but Azure Container Registry **Basic tier** only allows **10GB**.

## Solutions

### Option 1: Upgrade to Standard Tier (Easiest)

**Cost**: ~$25/month (vs ~$5/month for Basic)

1. In Azure Portal → Container Registry
2. Go to **"Settings"** → **"Pricing tier"**
3. Change from **Basic** to **Standard** (100GB limit)
4. Click **"Save"**

**Pros**: No code changes needed
**Cons**: Higher cost

---

### Option 2: Optimize Docker Image (Recommended)

Build a smaller image using the optimized Dockerfile:

```bash
# Build optimized image
docker build -f Dockerfile.optimized -t rag-chatbot-app:optimized .

# Check new size
docker images | grep rag-chatbot

# Test it works
docker run -p 8000:8000 rag-chatbot-app:optimized
```

**Expected size reduction**: 12.7GB → ~3-5GB

**Key optimizations**:
- Removed unnecessary cache files
- Cleaned up Python cache
- Excluded large data files from image
- Used multi-stage builds more efficiently

---

### Option 3: Use Azure File Share for Data

Instead of including data in the image:

1. **Don't copy `data/` directory** into the image
2. **Mount Azure File Share** at runtime for:
   - Knowledge base files
   - Vector store data
   - Output files

This reduces image size significantly.

---

### Option 4: Use .dockerignore

Create a `.dockerignore` file to exclude large files:

```bash
# Create .dockerignore
cat > .dockerignore << EOF
data/knowledge_base/**/*.pdf
data/knowledge_base/**/*.docx
data/knowledge_base/**/*.jpeg
data/knowledge_base/**/*.png
data/vector_store/*
output/*
.git
venv/
__pycache__/
*.pyc
*.pyo
EOF

# Rebuild
docker build -t rag-chatbot-app:latest .
```

---

## Recommended Approach

**For demo purposes**: Use **Option 1** (upgrade to Standard tier) - fastest and easiest.

**For production**: Use **Option 2** (optimize image) + **Option 4** (.dockerignore) to reduce costs.

---

## Quick Commands

```bash
# Check current image size
docker images rag-chatbot-app:latest

# Build optimized version
docker build -f Dockerfile.optimized -t rag-chatbot-app:optimized .

# Compare sizes
docker images | grep rag-chatbot

# Test optimized image
docker run -d -p 8000:8000 --name test-app rag-chatbot-app:optimized
docker logs test-app
docker stop test-app && docker rm test-app
```

---

## After Optimization

Once your image is under 10GB:

1. Tag and push to ACR:
```bash
ACR_NAME="ragchatbotacr"
docker tag rag-chatbot-app:optimized ${ACR_NAME}.azurecr.io/rag-chatbot-app:latest
docker push ${ACR_NAME}.azurecr.io/rag-chatbot-app:latest
```

2. Continue with deployment as per the guide.

