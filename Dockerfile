# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
ARG FRONTEND_BUILD_CACHE_BUSTER
COPY frontend/ai-chatbot-ui/package*.json ./
RUN npm ci --prefer-offline --no-audit
COPY frontend/ai-chatbot-ui/ ./
RUN npm run build

# Stage 2: Python dependencies layer (for better caching)
FROM python:3.11-slim AS python-deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Final image with everything consolidated
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Copy built frontend to nginx
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Remove default nginx config and copy our custom one
RUN rm -f /etc/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf

# Create required directories
RUN mkdir -p /app/data/vector_store /app/data/knowledge_base /app/output /app/data/chat_history

# Create startup script with proper error handling and timing
RUN echo '#!/bin/bash\n\
    set -e\n\
    \n\
    echo "Starting RAG Chatbot services..."\n\
    \n\
    # Start FastAPI in background first\n\
    echo "Starting FastAPI application..."\n\
    uvicorn src.chatbot_backend.rag_api:app --host 127.0.0.1 --port 8000 --workers 2 &\n\
    FASTAPI_PID=$!\n\
    \n\
    # Wait for FastAPI to be ready\n\
    echo "Waiting for FastAPI to start..."\n\
    for i in {1..30}; do\n\
    if curl -s http://127.0.0.1:8000/ > /dev/null; then\n\
    echo "FastAPI is ready!"\n\
    break\n\
    fi\n\
    echo "Waiting for FastAPI... ($i/30)"\n\
    sleep 1\n\
    done\n\
    \n\
    # Check if FastAPI actually started\n\
    if ! curl -s http://127.0.0.1:8000/ > /dev/null; then\n\
    echo "ERROR: FastAPI failed to start!"\n\
    exit 1\n\
    fi\n\
    \n\
    # Start Nginx in the foreground\n\
    echo "Starting Nginx..."\n\
    exec nginx -g "daemon off;"\n' > /app/startup.sh && chmod +x /app/startup.sh

EXPOSE 8000 80
CMD ["/app/startup.sh"]