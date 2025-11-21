# Stage 1: Build React Frontend
FROM node:20-alpine as frontend-build
WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/ai-chatbot-ui/package*.json ./
RUN npm config set fetch-retry-maxtimeout 600000 \
    && npm config set fetch-retry-mintimeout 10000 \
    && npm config set registry https://registry.npmjs.org/
RUN npm install

# Copy frontend source code
COPY frontend/ai-chatbot-ui/ .

# Build with empty API URL so requests are relative (same domain)
ENV VITE_API_URL=""
RUN npm run build

# Stage 2: Python Backend + Serving Frontend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (if any needed for python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY src/ ./src/
# COPY data/ ./data/

# Copy built frontend from Stage 1 to 'static' folder
# The backend code expects 'static/index.html' and 'static/assets'
COPY --from=frontend-build /app/frontend/dist ./static

# Expose port 8000 (FastAPI default)
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.chatbot_backend.rag_api:app", "--host", "0.0.0.0", "--port", "8000"]
