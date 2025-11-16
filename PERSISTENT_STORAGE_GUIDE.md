# Persistent Storage & Performance Optimization Guide

## Overview

This guide explains how the system now maintains persistent Qdrant database storage and improves backend loading speed.

## Persistent Storage Setup

### 1. Docker Compose Volume Configuration

The `docker-compose.yml` now includes:

```yaml
volumes:
  qdrant_storage:
    driver: local
```

This creates a named Docker volume that persists data even when containers are stopped or removed.

### 2. Qdrant Data Persistence

**Location**: `/qdrant/storage` inside container → `qdrant_storage` volume on host

**What's stored**:
- Vector embeddings
- Collection metadata
- Index files
- Write-ahead logs (WAL)

**Persistence guarantees**:
- Data survives container restart
- Data survives service restart
- Data survives host reboot (if volume is on persistent storage)

### 3. Application Data Volumes

```yaml
volumes:
  - ./data/knowledge_base:/app/data/knowledge_base      # Knowledge base documents
  - ./data/vector_store:/app/data/vector_store          # Backup vector store
  - ./output:/app/output                                 # Generated outputs
```

## Performance Optimizations

### 1. Docker Compose Improvements

**Health Checks**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```
- Ensures Qdrant is ready before app starts
- Prevents connection errors on startup

**Shared Memory**:
```yaml
shm_size: 2gb
```
- Allocates 2GB shared memory for faster operations
- Improves embedding and search performance

**Restart Policy**:
```yaml
restart: unless-stopped
```
- Automatically restarts services on failure
- Maintains uptime

### 2. Qdrant Configuration (`qdrant_config.yaml`)

**Performance Tuning**:
```yaml
performance:
  max_search_threads: 4
  max_update_threads: 4
  enable_simd: true
```
- Multi-threaded search operations
- SIMD optimizations for vector operations
- Faster similarity searches

**Storage Optimization**:
```yaml
storage:
  wal:
    enabled: true
    wal_capacity_mb: 200
```
- Write-ahead logging for durability
- Efficient disk usage

### 3. Dockerfile Optimizations

**Multi-stage Build**:
- Reduces final image size
- Faster builds with layer caching
- Separates build dependencies from runtime

**Python Dependencies Layer**:
```dockerfile
FROM python:3.11-slim AS python-deps
```
- Cached separately for faster rebuilds
- Only rebuilds if requirements.txt changes

**Uvicorn Configuration**:
```bash
uvicorn src.chatbot_backend.rag_api:app --host 0.0.0.0 --port 8000 --workers 2 --loop uvloop
```
- 2 worker processes for parallel request handling
- uvloop for faster event loop
- Improves throughput

### 4. Backend Loading Speed Improvements

**Lazy Loading**:
- Vectorstore initialized on first use
- Embeddings model cached in memory
- Reduces startup time

**Connection Pooling**:
- Qdrant client reuses connections
- Reduces connection overhead

**Caching Strategy**:
- Config singleton pattern
- Vectorstore cached globally
- Embeddings model cached

## Usage Instructions

### Starting Services

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
docker-compose logs -f qdrant
```

### Verifying Persistent Storage

```bash
# Check Docker volumes
docker volume ls | grep qdrant

# Inspect volume details
docker volume inspect qdrant_storage

# View volume location on host
docker volume inspect qdrant_storage --format='{{.Mountpoint}}'
```

### Testing Persistence

1. **Add data to Qdrant**:
   ```bash
   # Ingest knowledge base
   curl -X POST http://localhost:8000/ingest
   ```

2. **Stop services**:
   ```bash
   docker-compose down
   ```

3. **Restart services**:
   ```bash
   docker-compose up -d
   ```

4. **Verify data persists**:
   ```bash
   # Query should return same results
   curl -X POST http://localhost:8000/chat_response \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "session_id": "test"}'
   ```

## Environment Variables

Add to `.env` file:

```bash
# Qdrant Configuration
QDRANT_HOST=qdrant_db
QDRANT_PORT=6333
QDRANT_COLLECTION=rag_collection
QDRANT_CHAT_HISTORY_COLLECTION=chatbot_chat_history

# Performance
RETRIEVER_TOP_K=10
CHUNK_SIZE=800
CHUNK_OVERLAP=150

# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

## Monitoring & Maintenance

### Check Qdrant Health

```bash
# Health endpoint
curl http://localhost:6333/health

# Collection info
curl http://localhost:6333/collections/rag_collection
```

### View Storage Usage

```bash
# Check volume size
docker volume inspect qdrant_storage --format='{{.Mountpoint}}' | xargs du -sh

# Check container logs for storage info
docker-compose logs qdrant | grep -i storage
```

### Backup Strategy

**Manual Backup**:
```bash
# Create snapshot
docker exec qdrant_db curl -X POST http://localhost:6333/snapshots

# Copy volume to backup location
docker run --rm -v qdrant_storage:/data -v /backup:/backup \
  alpine tar czf /backup/qdrant_backup.tar.gz -C /data .
```

**Automated Backup** (optional):
- Use Docker volume backup tools
- Schedule periodic snapshots
- Store backups in cloud storage

## Troubleshooting

### Issue: Data not persisting

**Solution**:
```bash
# Check volume exists
docker volume ls | grep qdrant_storage

# Check volume mount in container
docker inspect qdrant_db | grep -A 5 Mounts

# Verify permissions
docker exec qdrant_db ls -la /qdrant/storage
```

### Issue: Slow performance

**Solution**:
1. Check shared memory allocation: `docker stats`
2. Verify Qdrant config is loaded: `docker logs qdrant_db`
3. Monitor CPU/Memory: `docker stats`
4. Check network latency: `docker exec app ping qdrant_db`

### Issue: Connection refused

**Solution**:
```bash
# Wait for Qdrant to be ready
docker-compose logs qdrant | grep "listening"

# Check health
curl http://localhost:6333/health

# Restart services
docker-compose restart
```

## Performance Benchmarks

Expected improvements:

| Metric | Before | After |
|--------|--------|-------|
| Startup time | ~30s | ~15s |
| First query | ~5s | ~2s |
| Subsequent queries | ~2s | ~0.5s |
| Data persistence | ❌ | ✅ |
| Concurrent requests | 1 | 2+ |

## Best Practices

1. **Regular Backups**: Schedule weekly backups of Qdrant volume
2. **Monitor Storage**: Keep track of volume size growth
3. **Update Regularly**: Keep Docker images updated
4. **Resource Allocation**: Allocate sufficient CPU/Memory
5. **Network**: Use Docker network for inter-service communication
6. **Logging**: Enable structured logging for debugging

## Advanced Configuration

### Scaling Qdrant

For larger datasets, consider:
- Increasing `max_search_threads`
- Increasing `wal_capacity_mb`
- Using SSD storage for volume
- Enabling Qdrant clustering

### Custom Qdrant Config

Edit `qdrant_config.yaml` and rebuild:
```bash
docker-compose down
# Edit qdrant_config.yaml
docker-compose up -d --build
```

## References

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Docker Volumes](https://docs.docker.com/storage/volumes/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Uvicorn Configuration](https://www.uvicorn.org/)
