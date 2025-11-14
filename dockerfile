# ==============================
# Stage 1: Build Environment
# ==============================
FROM python:3.12-slim AS base

# Prevent interactive prompts during install
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Copy requirements (so Docker caching works better)
COPY requirements.txt .

# Install dependencies safely
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --upgrade pip && \
    apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# ==============================
# Stage 2: Runtime
# ==============================
FROM python:3.12-slim

WORKDIR /app

# Copy installed dependencies from build stage
COPY --from=base /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=base /usr/local/bin /usr/local/bin

# Copy app source
COPY . .

# Expose your app port (change if needed)
EXPOSE 8000

# Environment variables (override from docker-compose)
ENV QDRANT_URL=https://qdrant-app.politewave-6298a03c.eastus.azurecontainerapps.io
ENV QDRANT_API_KEY=""
ENV PYTHONUNBUFFERED=1

# Add basic error handling on startup
# CMD ["bash", "-c", "python main.py || { echo '❌ App crashed! Check logs.'; sleep 10; exit 1; }"]
