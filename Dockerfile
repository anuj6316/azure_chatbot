# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/ai-chatbot-ui/package*.json ./
RUN npm ci
COPY frontend/ai-chatbot-ui/ ./
RUN npm run build

# Stage 2: Final image with everything consolidated
FROM python:3.11-slim
WORKDIR /app

# Install Qdrant + Nginx
RUN apt-get update && apt-get install -y curl nginx \
    && curl -L https://github.com/qdrant/qdrant/releases/download/v1.7.4/qdrant-x86_64-unknown-linux-gnu.tar.gz | tar xz \
    && mv qdrant /usr/local/bin/ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (FIXES uvicorn error)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Copy built frontend to nginx
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create Qdrant config
RUN echo 'storage:\n  path: /app/data/vector_store' > /app/qdrant-config.yaml

# Create startup script for all services
RUN echo '#!/bin/bash\n\
    set -e\n\
    mkdir -p /app/data/vector_store\n\
    qdrant --config-path /app/qdrant-config.yaml &\n\
    sleep 10\n\
    service nginx start &\n\
    exec uvicorn src.chatbot_backend.rag_api:app --host 0.0.0.0 --port 8000\n' > /app/startup.sh && chmod +x /app/startup.sh

EXPOSE 6333 8000 80
CMD ["/app/startup.sh"]
