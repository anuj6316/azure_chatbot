# =========================
# Python Dependencies Stage
# =========================
FROM python:3.12-slim AS python-deps

WORKDIR /app

# Install dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# =========================
# Backend Stage
# =========================
FROM python:3.12-slim AS backend

WORKDIR /app

# Copy Python dependencies from the python-deps stage
COPY --from=python-deps /root/.local /root/.local

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/chatbot_backend/ ./src/chatbot_backend/
COPY src/core/ ./src/core/

# Expose FastAPI port
EXPOSE 8000

# Command to start FastAPI
CMD ["uvicorn", "src.chatbot_backend.rag_api:app", "--host", "0.0.0.0", "--port", "8000"]

# =========================
# Frontend Stage
# =========================
FROM node:20-alpine AS frontend

WORKDIR /app

# Copy package files
COPY frontend/ai-chatbot-ui/package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY frontend/ai-chatbot-ui/ .

# Build the application
RUN npm run build

# Expose port
EXPOSE 5173

# Run development server
CMD ["npm", "run", "dev"]