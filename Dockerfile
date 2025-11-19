# ==========================================
# Stage 1: Build React frontend
# ==========================================
FROM node:18-alpine AS frontend-builder

# Set working directory for the frontend build
WORKDIR /app/frontend

# Copy package.json files first to leverage Docker cache for dependencies
# NOTE: Ensure 'frontend/ai-chatbot-ui/' matches your actual folder structure
COPY frontend/ai-chatbot-ui/package*.json ./ 

# Install dependencies (clean install)
RUN npm ci --prefer-offline --no-audit 

# Copy the rest of the frontend source code
COPY frontend/ai-chatbot-ui/ ./ 

# Build the React application
# This typically creates a 'dist' or 'build' folder
RUN npm run build 

# ==========================================
# Stage 2: Final Python image
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (Curl is required for the healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* 

# Copy Python requirements
COPY requirements.txt . 

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt 

# Copy the backend application code
COPY src/ ./src/ 

# Copy the built frontend assets from the builder stage
# We copy them into './static' so FastAPI can serve them
COPY --from=frontend-builder /app/frontend/dist ./static 

# Create directory for local SQLite storage (if used)
RUN mkdir -p /app/data/chat_history 

# Expose the port the app runs on
EXPOSE 8000 

# Health check to ensure the API is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1 

# Start the application
CMD ["uvicorn", "src.chatbot_backend.rag_api:app", "--host", "0.0.0.0", "--port", "8000"] 