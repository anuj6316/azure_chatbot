#!/bin/bash

# Setup Persistent Storage and Performance Optimization Script
# This script sets up Docker volumes and configurations for persistent Qdrant storage

set -e

echo "=========================================="
echo "Setting up Persistent Storage & Performance"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${BLUE}Step 1: Creating necessary directories...${NC}"
mkdir -p data/knowledge_base
mkdir -p data/vector_store
mkdir -p output
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

echo -e "${BLUE}Step 2: Checking Docker volumes...${NC}"
if docker volume ls | grep -q qdrant_storage; then
    echo -e "${GREEN}✓ Qdrant storage volume already exists${NC}"
else
    echo -e "${YELLOW}Creating qdrant_storage volume...${NC}"
    docker volume create qdrant_storage
    echo -e "${GREEN}✓ Qdrant storage volume created${NC}"
fi
echo ""

echo -e "${BLUE}Step 3: Verifying docker-compose.yml...${NC}"
if [ -f "docker-compose.yml" ]; then
    echo -e "${GREEN}✓ docker-compose.yml found${NC}"
else
    echo -e "${YELLOW}docker-compose.yml not found!${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}Step 4: Verifying qdrant_config.yaml...${NC}"
if [ -f "qdrant_config.yaml" ]; then
    echo -e "${GREEN}✓ qdrant_config.yaml found${NC}"
else
    echo -e "${YELLOW}qdrant_config.yaml not found!${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}Step 5: Checking .env file...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file found${NC}"
    echo "  Current settings:"
    grep -E "QDRANT|CHUNK|RETRIEVER" .env || echo "  (No Qdrant settings found)"
else
    echo -e "${YELLOW}Creating .env file with defaults...${NC}"
    cat > .env << 'EOF'
# LLM Configuration
MODEL_NAME=gemini-2.0-flash
GOOGLE_API_KEY=your_api_key_here

# Qdrant Configuration
QDRANT_HOST=qdrant_db
QDRANT_PORT=6333
QDRANT_COLLECTION=rag_collection
QDRANT_CHAT_HISTORY_COLLECTION=chatbot_chat_history

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Retrieval Settings
RETRIEVER_TOP_K=10
CHUNK_SIZE=800
CHUNK_OVERLAP=150

# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000

# CORS
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true
EOF
    echo -e "${GREEN}✓ .env file created with defaults${NC}"
fi
echo ""

echo -e "${BLUE}Step 6: Building Docker images...${NC}"
docker-compose build
echo -e "${GREEN}✓ Docker images built${NC}"
echo ""

echo -e "${BLUE}Step 7: Starting services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"
echo ""

echo -e "${BLUE}Step 8: Waiting for services to be ready...${NC}"
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Services are running${NC}"
else
    echo -e "${YELLOW}Services may not be fully ready yet. Checking logs...${NC}"
    docker-compose logs
fi
echo ""

echo -e "${BLUE}Step 9: Verifying Qdrant connectivity...${NC}"
if curl -s http://localhost:6333/health > /dev/null; then
    echo -e "${GREEN}✓ Qdrant is healthy${NC}"
else
    echo -e "${YELLOW}Qdrant health check failed. It may still be starting...${NC}"
fi
echo ""

echo -e "${BLUE}Step 10: Displaying volume information...${NC}"
echo "Qdrant Storage Volume:"
docker volume inspect qdrant_storage --format='  Location: {{.Mountpoint}}'
docker volume inspect qdrant_storage --format='  Driver: {{.Driver}}'
echo ""

echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Services are running at:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - Qdrant: http://localhost:6333"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo "  - Check volume: docker volume inspect qdrant_storage"
echo ""
echo "For more information, see PERSISTENT_STORAGE_GUIDE.md"
echo ""
