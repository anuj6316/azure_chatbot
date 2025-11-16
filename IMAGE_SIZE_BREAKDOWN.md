# Docker Image Size Breakdown

## Current Image Size
- **Uncompressed**: 12.2GB
- **Compressed** (what gets pushed to ACR): 4.32GB ✅ **This fits in Basic tier!**

## What's Taking Up Space?

### 1. Python Dependencies (~8-10GB uncompressed)

#### Biggest Culprits:

**🔴 sentence-transformers==3.2.1** (~2-3GB)
- Downloads pre-trained ML models (embeddings)
- Models stored in: `~/.cache/huggingface/` or `/root/.cache/huggingface/`
- Default model `all-MiniLM-L6-v2` is ~90MB, but the library includes dependencies

**🔴 pandas==2.2.3** (~500MB-1GB)
- Large data science library with many dependencies
- Includes NumPy, which is also large

**🔴 pymupdf==1.24.13** (~200-300MB)
- PDF processing library
- Includes compiled binaries

**🔴 langchain ecosystem** (~1-2GB total)
- `langchain==0.3.7`
- `langchain-core==0.3.17`
- `langchain-community==0.3.7`
- `langchain-huggingface==0.1.2`
- `langchain-google-genai==2.0.7`
- `langchain-openai`
- `langchain-qdrant==0.1.4`
- `langchain-azure-ai`

**🟡 Other large packages:**
- `pdf2image` + dependencies (~100-200MB)
- `Pillow==11.0.0` (~50-100MB)
- `azure-ai-vision-imageanalysis` (~100MB)
- `google-genai` (~50-100MB)

### 2. Base Image (~200-300MB)
- `python:3.11-slim` base image

### 3. System Dependencies (~50-100MB)
- nginx
- curl
- apt packages

### 4. Application Code (~10-50MB)
- Your Python source code
- Frontend build (React dist)
- Configuration files

### 5. Python Runtime (~100-200MB)
- Python 3.11 interpreter
- Standard library

---

## Why Compressed Size is Smaller?

When you push to Azure Container Registry:
- Docker compresses layers
- Duplicate files are deduplicated
- **Result**: 12.2GB → 4.32GB compressed ✅

**Good News**: ACR Basic tier (10GB) accepts **compressed size**, so **4.32GB fits!**

---

## How to Reduce Size Further (Optional)

### Option 1: Remove Unused Dependencies

Check if you're using all packages:

```bash
# Check which packages you actually import
grep -r "import\|from" src/ | grep -E "(pandas|pdf2image|python-magic)" | head -20
```

If not used, remove from `requirements.txt`.

### Option 2: Use Lazy Model Loading

Instead of downloading models at build time, download at runtime:

```python
# In your code, models download on first use
# This keeps image smaller, but first request is slower
```

### Option 3: Use Alpine-based Python Image

```dockerfile
FROM python:3.11-alpine  # Smaller base (~50MB vs ~200MB)
```

**Warning**: Some packages may not work with Alpine (musl libc vs glibc).

### Option 4: Multi-stage Build Optimization

Already done in `Dockerfile.optimized`, but can be improved further.

### Option 5: Remove Development Dependencies

If any packages are only for development, move them to `requirements-dev.txt`.

---

## Size Comparison

| Component | Uncompressed | Compressed (ACR) |
|-----------|--------------|------------------|
| Python deps | ~8-10GB | ~3-4GB |
| Base image | ~300MB | ~100MB |
| System deps | ~100MB | ~50MB |
| App code | ~50MB | ~20MB |
| **Total** | **~12.2GB** | **~4.32GB** ✅ |

---

## Recommendation

**Your compressed size (4.32GB) fits in Azure Container Registry Basic tier (10GB limit)!**

You can proceed with deployment. The 12.2GB you see is the uncompressed size, which is normal.

If you want to reduce further:
1. Remove unused packages from `requirements.txt`
2. Use Alpine base (if compatible)
3. Lazy-load models at runtime

But for now, **4.32GB compressed is fine for Basic tier!** ✅

