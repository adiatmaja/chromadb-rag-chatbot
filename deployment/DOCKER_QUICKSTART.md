# Docker Quick Start Guide

Fast guide to build and run the RAG system in Docker.

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Build the image (3-5 minutes)
docker-compose build

# 2. Run the container
docker-compose up

# 3. (Optional) Run in background
docker-compose up -d
```

---

## 📋 Prerequisites

- Docker Desktop or Docker Engine installed
- At least 4GB RAM available
- 5GB free disk space

---

## 🔧 Build Options

### Fast Build (Recommended)
```bash
docker-compose build
```

### Clean Build (If having issues)
```bash
docker-compose build --no-cache
```

### With BuildKit (Fastest)
```bash
set DOCKER_BUILDKIT=1
docker-compose build
```

---

## ▶️ Running the Container

### Interactive Mode
```bash
docker-compose up
```
Press `Ctrl+C` to stop.

### Background Mode
```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Run Specific Scripts
```bash
# Index products
docker-compose run --rm rag python scripts/indexing/index_products.py

# Index intents
docker-compose run --rm rag python scripts/indexing/index_intent.py

# Run tests
docker-compose run --rm rag python scripts/testing/verify_collections.py
```

---

## 🐛 Troubleshooting

### Issue: "onnxruntime error"
**Solution**: Already fixed! The system uses PyTorch backend instead.

### Issue: Build is slow (30+ minutes)
**Solution**:
1. Enable BuildKit: `set DOCKER_BUILDKIT=1`
2. Check internet connection speed
3. Use a faster PyPI mirror (edit Dockerfile)

### Issue: Container won't start
```bash
# Check logs
docker-compose logs rag

# Verify configuration
docker-compose exec rag python -m src.config
```

### Issue: Permission denied
```bash
# Fix volume permissions (Linux/Mac)
sudo chown -R 1000:1000 database/ data/ logs/

# Or run as root (not recommended)
docker-compose run --user root rag bash
```

---

## 📦 Data Management

### Initial Setup (First Time)
```bash
# Access container shell
docker-compose exec rag bash

# Inside container, index data
python scripts/indexing/index_products.py
python scripts/indexing/parse_intent_data.py
python scripts/indexing/index_intent.py

# Exit container
exit
```

### Update Data Files
```bash
# Edit data files on host
nano data/product_data.csv
nano data/intent.txt

# Reindex in container
docker-compose exec rag python scripts/indexing/index_products.py
docker-compose exec rag python scripts/indexing/index_intent.py
```

### Backup Database
```bash
# Create backup
tar -czf rag-backup-$(date +%Y%m%d).tar.gz database/ data/

# Restore backup
tar -xzf rag-backup-20251117.tar.gz
```

---

## 🔍 Common Commands

```bash
# Build image
docker-compose build

# Start container
docker-compose up

# Start in background
docker-compose up -d

# Stop container
docker-compose down

# View logs
docker-compose logs -f rag

# Access shell
docker-compose exec rag bash

# Run Python script
docker-compose exec rag python your_script.py

# Restart container
docker-compose restart

# Remove everything (including volumes!)
docker-compose down -v  # ⚠️ WARNING: Deletes database!
```

---

## 📊 Monitoring

### View Logs
```bash
# Real-time logs
docker-compose logs -f rag

# Last 100 lines
docker-compose logs --tail=100 rag

# Logs since specific time
docker-compose logs --since 2024-11-17T10:00:00 rag
```

### Check Resources
```bash
# Real-time stats
docker stats rag-product-search

# Container info
docker inspect rag-product-search

# Health status
docker inspect --format='{{.State.Health.Status}}' rag-product-search
```

---

## 🎯 Production Deployment

### Build for Production
```bash
# Tag image
docker build -t your-registry/rag-product-search:v2.0 .

# Push to registry
docker push your-registry/rag-product-search:v2.0
```

### Deploy on Server
```bash
# Pull image
docker pull your-registry/rag-product-search:v2.0

# Run with production config
docker run -d \
  --name rag-system \
  -v $(pwd)/database:/app/database \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env:ro \
  --restart unless-stopped \
  your-registry/rag-product-search:v2.0
```

---

## ⚙️ Configuration

### Environment Variables

Edit `.env` file or pass via docker-compose:

```env
# LLM Configuration (use host.docker.internal for LLM on host)
LLM_BASE_URL=http://host.docker.internal:1234/v1
LLM_MODEL_NAME=gemma-2b-it
LLM_API_KEY=lm-studio

# Embedding Model
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# Collections
COLLECTION_NAME=fmcg_products
FAQ_COLLECTION_NAME=faq_collection
INTENT_COLLECTION_NAME=intent_collection

# Retrieval
RETRIEVAL_TOP_K=3
```

### Custom Command
```bash
# Override default command
docker-compose run --rm rag python scripts/demo/demo_full_workflow.py
```

---

## 🆘 Getting Help

1. **Check logs first**: `docker-compose logs rag`
2. **Verify config**: `docker-compose exec rag python -m src.config`
3. **Test collections**: `docker-compose exec rag python scripts/testing/verify_collections.py`
4. **Access shell**: `docker-compose exec rag bash`

---

## 📚 Next Steps

- [Full Docker Documentation](DOCKER.md)
- [Build Optimization Guide](BUILD_OPTIMIZATION.md)
- [Main README](../README.md)
- [Developer Guide](../CLAUDE.md)

---

**Build Time**: ~3-5 minutes (first build)
**Container Size**: ~3GB
**Status**: Production Ready 🐳
