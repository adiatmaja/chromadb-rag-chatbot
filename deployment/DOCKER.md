# Docker Deployment Guide

Complete guide for deploying the RAG Product Search & Intent Classification System using Docker.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Building the Image](#building-the-image)
- [Running the Container](#running-the-container)
- [Data Management](#data-management)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Required Software

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher (optional but recommended)

### System Requirements

- **RAM**: Minimum 4GB (8GB recommended)
- **CPU**: 2+ cores recommended
- **Storage**: ~5GB for image and data

### Installation

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker-compose --version
```

---

## 🚀 Quick Start

### 1. Prepare the Environment

```bash
# Navigate to project directory
cd /path/to/nlp

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Build and Run

**Option A: Using Docker Compose (Recommended)**

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f rag

# Stop the container
docker-compose down
```

**Option B: Using Docker CLI**

```bash
# Build the image
docker build -t rag-product-search:latest .

# Run the container
docker run -it --rm \
  --name rag-system \
  -v $(pwd)/database:/app/database \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env:ro \
  --add-host host.docker.internal:host-gateway \
  rag-product-search:latest
```

### 3. Index Data (First Time Setup)

```bash
# Access container shell
docker-compose exec rag bash

# Inside container, run indexing scripts
python scripts/indexing/parse_intent_data.py
python scripts/indexing/index_intent.py
python scripts/indexing/index_products.py
python scripts/indexing/index_faq.py  # Optional, requires ClickHouse

# Exit container
exit
```

### 4. Run Interactive Query System

```bash
# The container starts with interactive query system by default
docker-compose up

# Or attach to running container
docker attach rag-product-search
```

---

## ⚙️ Configuration

### Environment Variables

Edit `.env` file with your configuration:

```env
# =============================================================================
# LLM Configuration
# =============================================================================
# Use host.docker.internal to access LLM running on host machine
LLM_BASE_URL=http://host.docker.internal:1234/v1
LLM_MODEL_NAME=gemma-2b-it
LLM_API_KEY=lm-studio
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=1000

# =============================================================================
# Embedding Model
# =============================================================================
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# =============================================================================
# Vector Database Collections
# =============================================================================
COLLECTION_NAME=fmcg_products
FAQ_COLLECTION_NAME=faq_collection
INTENT_COLLECTION_NAME=intent_collection
RETRIEVAL_TOP_K=3

# =============================================================================
# ClickHouse Configuration (Optional - for FAQ system)
# =============================================================================
CLICKHOUSE_HOST=your-clickhouse-host
CLICKHOUSE_PORT=8123
CLICKHOUSE_DB_NAME=your_database

# =============================================================================
# Application Settings
# =============================================================================
LOG_LEVEL=INFO
ENABLE_RICH_CONSOLE=true
```

### Connecting to External LLM

**LLM on Host Machine:**
```env
LLM_BASE_URL=http://host.docker.internal:1234/v1
```

**LLM on Network:**
```env
LLM_BASE_URL=http://192.168.1.100:1234/v1
```

**Cloud LLM (OpenAI, etc.):**
```env
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-actual-api-key
LLM_MODEL_NAME=gpt-3.5-turbo
```

---

## 🏗️ Building the Image

### Basic Build

```bash
docker build -t rag-product-search:latest .
```

### Build with Custom Tag

```bash
docker build -t rag-product-search:v2.0 .
```

### Build with No Cache (Clean Build)

```bash
docker build --no-cache -t rag-product-search:latest .
```

### Multi-Platform Build (for deployment)

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -t rag-product-search:latest .
```

---

## 🐳 Running the Container

### Interactive Mode (Default)

```bash
# Using Docker Compose
docker-compose up

# Using Docker CLI
docker run -it --rm \
  --name rag-system \
  -v $(pwd)/database:/app/database \
  -v $(pwd)/data:/app/data \
  rag-product-search:latest
```

### Background Mode (Daemon)

```bash
# Using Docker Compose
docker-compose up -d

# Using Docker CLI
docker run -d \
  --name rag-system \
  -v $(pwd)/database:/app/database \
  -v $(pwd)/data:/app/data \
  rag-product-search:latest
```

### Run Specific Scripts

```bash
# Run demo workflow
docker-compose run --rm rag python scripts/demo/demo_full_workflow.py

# Run tests
docker-compose run --rm rag python scripts/testing/verify_collections.py

# Test stock reader
docker-compose run --rm rag python -m src.utils.stock_reader
```

### Access Container Shell

```bash
# Using Docker Compose
docker-compose exec rag bash

# Using Docker CLI
docker exec -it rag-system bash
```

---

## 💾 Data Management

### Volume Mounts

The Docker setup uses volume mounts for data persistence:

```yaml
volumes:
  - ./database:/app/database  # ChromaDB vector database
  - ./data:/app/data          # CSV data files
  - ./logs:/app/logs          # Application logs
```

### Backup Data

```bash
# Backup vector database
docker-compose exec rag tar -czf /app/backup.tar.gz /app/database

# Copy backup to host
docker cp rag-product-search:/app/backup.tar.gz ./backup.tar.gz

# Or backup using host filesystem
tar -czf rag-backup-$(date +%Y%m%d).tar.gz database/ data/
```

### Restore Data

```bash
# Copy backup to container
docker cp ./backup.tar.gz rag-product-search:/app/

# Extract inside container
docker-compose exec rag tar -xzf /app/backup.tar.gz -C /app/

# Or restore using host filesystem
tar -xzf rag-backup-20251114.tar.gz
```

### Update Data Files

```bash
# Update stock data
nano data/stock_data.csv

# Update product data
nano data/product_data.csv

# Restart container to pick up changes (if needed)
docker-compose restart rag
```

---

## 🔬 Advanced Usage

### Custom Entrypoint

```bash
# Run custom Python script
docker-compose run --rm rag python your_script.py

# Run bash commands
docker-compose run --rm rag bash -c "ls -la /app/database"
```

### Resource Limits

Edit `docker-compose.yml` to adjust resource limits:

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # Use 4 CPU cores
      memory: 8G       # Use 8GB RAM
    reservations:
      cpus: '2.0'      # Reserve 2 cores
      memory: 4G       # Reserve 4GB RAM
```

### Network Configuration

**Access Host Services:**
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

**Connect Multiple Containers:**
```yaml
networks:
  rag-network:
    driver: bridge
```

### Health Checks

Monitor container health:

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' rag-product-search

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' rag-product-search
```

---

## 🐛 Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs rag
```

**Verify configuration:**
```bash
docker-compose exec rag python -m src.config
```

**Check volumes:**
```bash
docker volume ls
docker volume inspect nlp_rag_database
```

### LLM Connection Issues

**Test connectivity from container:**
```bash
docker-compose exec rag curl http://host.docker.internal:1234/v1/models
```

**Update LLM URL:**
```env
# In .env file
LLM_BASE_URL=http://host.docker.internal:1234/v1
```

### Permission Issues

**Fix volume permissions:**
```bash
sudo chown -R 1000:1000 database/ data/ logs/
```

**Run as different user:**
```bash
docker-compose run --user root rag bash
```

### Out of Memory

**Increase Docker memory limit:**
```bash
# Docker Desktop: Settings > Resources > Memory
# Or in docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 8G
```

### Vector Database Issues

**Reset ChromaDB:**
```bash
# Stop container
docker-compose down

# Remove database
rm -rf database/chroma_db/*

# Rebuild indexes
docker-compose run --rm rag bash -c "
  python scripts/indexing/index_products.py && \
  python scripts/indexing/index_intent.py
"
```

### Container Keeps Restarting

**Disable auto-restart:**
```yaml
restart: "no"  # In docker-compose.yml
```

**Check health status:**
```bash
docker inspect rag-product-search | grep -A 10 Health
```

---

## 📊 Monitoring

### View Logs

```bash
# All logs
docker-compose logs -f rag

# Last 100 lines
docker-compose logs --tail=100 rag

# Since specific time
docker-compose logs --since 2024-11-14T10:00:00 rag
```

### Resource Usage

```bash
# Real-time stats
docker stats rag-product-search

# Resource summary
docker-compose top
```

### Container Status

```bash
# List containers
docker-compose ps

# Detailed inspection
docker inspect rag-product-search

# Health check status
docker inspect --format='{{.State.Health}}' rag-product-search
```

---

## 🚀 Production Deployment

### Build for Production

```bash
# Build optimized image
docker build --target runtime -t rag-product-search:v2.0-prod .

# Tag for registry
docker tag rag-product-search:v2.0-prod your-registry/rag-product-search:v2.0

# Push to registry
docker push your-registry/rag-product-search:v2.0
```

### Deploy on Server

```bash
# SSH to server
ssh user@your-server

# Pull image
docker pull your-registry/rag-product-search:v2.0

# Run with production config
docker-compose -f docker-compose.prod.yml up -d
```

### Auto-Start on Boot

```bash
# Enable Docker service
sudo systemctl enable docker

# Set restart policy
docker update --restart=unless-stopped rag-product-search
```

---

## 📝 Common Commands Cheat Sheet

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f rag

# Shell access
docker-compose exec rag bash

# Run script
docker-compose run --rm rag python scripts/run_query.py

# Rebuild
docker-compose build --no-cache

# Update and restart
docker-compose pull && docker-compose up -d

# Clean up
docker-compose down -v  # Warning: removes volumes!
```

---

## 🔐 Security Best Practices

1. **Don't commit `.env` file** - Contains sensitive data
2. **Use secrets management** for production
3. **Run as non-root user** (already configured)
4. **Keep images updated** - Rebuild regularly
5. **Scan for vulnerabilities:**
   ```bash
   docker scan rag-product-search:latest
   ```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices for Docker](https://docs.docker.com/develop/dev-best-practices/)

---

**Need Help?**
- Check the main [README.md](README.md)
- Review [CLAUDE.md](CLAUDE.md) for development guidelines
- Open an issue on GitHub

---

**Version**: 2.0.0
**Last Updated**: November 2025
**Status**: Production Ready 🐳
