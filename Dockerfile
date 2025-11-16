# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
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

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create Qdrant config directory
RUN mkdir -p /app/data/vector_store /app/data/knowledge_base /app/output

# Create startup script for all services
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Log startup\n\
echo "Starting RAG Chatbot services..."\n\
\n\
# Ensure directories exist\n\
mkdir -p /app/data/vector_store /app/data/knowledge_base /app/output\n\
\n\
# Start Nginx in background\n\
echo "Starting Nginx..."\n\
service nginx start\n\
\n\
# Start FastAPI application\n\
echo "Starting FastAPI application..."\n\
exec uvicorn src.chatbot_backend.rag_api:app --host 0.0.0.0 --port 8000 --workers 2\n' > /app/startup.sh && chmod +x /app/startup.sh

EXPOSE 6333 8000 80
CMD ["/app/startup.sh"]
