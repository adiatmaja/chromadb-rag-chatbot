# Docker Quick Start - Testing Commands

Copy and paste these commands to test Docker on your Windows PC.

---

## 📋 Prerequisites

Open PowerShell and navigate to project:
```powershell
cd C:\Users\adi\PycharmProjects\nlp
```

---

## ⚡ Step-by-Step Commands

### Step 1: Verify Docker Installation

```powershell
# Check Docker is installed and running
docker --version
docker-compose --version

# Should show:
# Docker version 20.x.x or higher
# Docker Compose version 2.x.x or higher
```

### Step 2: Run Quick Verification

```powershell
# Run verification script
.\verify_docker.bat
```

**Expected output:**
- ✅ Docker installation check
- Status of image and container
- Data files verification

### Step 3: Build Docker Image

```powershell
# Build the image (takes 10-20 minutes first time)
.\deploy.bat build

# OR using docker directly:
docker build -t rag-product-search:latest .
```

**Wait for:** `Successfully tagged rag-product-search:latest`

**To monitor build progress:**
```powershell
# In another PowerShell window
docker images | findstr rag
```

### Step 4: Verify Image Was Created

```powershell
# List Docker images
docker images

# Look for:
# rag-product-search   latest   <image-id>   <time>   <size>
```

### Step 5: Start the Container

```powershell
# Start container in background
.\deploy.bat start

# OR using docker-compose:
docker-compose up -d
```

**Expected output:**
- Container `rag-product-search` created
- Container started successfully

### Step 6: Check Container Status

```powershell
# Check if container is running
.\deploy.bat status

# OR:
docker ps
docker ps -a

# Should show:
# rag-product-search   Up X seconds   healthy
```

### Step 7: View Container Logs

```powershell
# View logs (Ctrl+C to exit)
.\deploy.bat logs

# OR:
docker-compose logs -f rag
```

**Look for:**
- ✅ "Unified RAG Orchestrator ready!"
- ✅ "Stock data loaded (30 entries)"
- ✅ Collections loaded messages

### Step 8: Access Container Shell

```powershell
# Enter container bash shell
.\deploy.bat shell

# OR:
docker-compose exec rag bash

# You should see:
# raguser@<container-id>:/app$
```

**Inside container, test:**
```bash
# Check Python version
python --version

# List files
ls -la

# Check data files
ls -la data/

# Test Python imports
python -c "from src.core.retriever import UnifiedRetriever; print('✓ OK')"

# Exit container
exit
```

### Step 9: Index Data (First Time Only)

```powershell
# Index all data using helper script
.\deploy.bat index
```

**This runs:**
1. Parse intent data
2. Index intents to ChromaDB
3. Index products to ChromaDB

**Expected output:**
- ✅ Intent data parsed successfully
- ✅ 35 intents indexed
- ✅ 11 products indexed

**OR manually:**
```powershell
docker-compose exec rag python scripts/indexing/parse_intent_data.py
docker-compose exec rag python scripts/indexing/index_intent.py
docker-compose exec rag python scripts/indexing/index_products.py
```

### Step 10: Verify Indexing

```powershell
# Check database directory
dir database\chroma_db

# Should see ChromaDB files and directories
```

### Step 11: Test Stock Reader

```powershell
# Run stock reader test
.\deploy.bat test

# OR:
docker-compose run --rm rag python -m src.utils.stock_reader
```

**Expected output:**
- ✅ Stock data loaded successfully
- ✅ Total rows: 30
- ✅ 4 test cases passing
- ✅ All tests completed

### Step 12: Verify Collections

```powershell
# Run collection verification
docker-compose exec rag python scripts/testing/verify_collections.py
```

**Expected output:**
- ✅ Product collection: 11 products loaded
- ✅ FAQ collection: 29 FAQs loaded
- ✅ Intent collection: 35 intents loaded
- ✅ Test queries successful

### Step 13: Run Demo Workflow

```powershell
# Run full demo (requires LLM - may fail if LLM not running)
.\deploy.bat demo

# OR:
docker-compose run --rm rag python scripts/demo/demo_full_workflow.py
```

**Note:** This will show "LLM connection error" if LM Studio is not running, but retrieval should still work.

---

## 🎯 Quick Test Sequence (Copy All)

```powershell
# Navigate to project
cd C:\Users\adi\PycharmProjects\nlp

# Verify setup
.\verify_docker.bat

# Build image (wait for completion)
.\deploy.bat build

# Verify image created
docker images | findstr rag-product-search

# Start container
.\deploy.bat start

# Check status
.\deploy.bat status

# Index data
.\deploy.bat index

# Test stock reader
.\deploy.bat test

# Verify collections
docker-compose exec rag python scripts/testing/verify_collections.py

# View logs
.\deploy.bat logs
```

---

## 🔍 Troubleshooting Commands

### Container Won't Start

```powershell
# Check logs for errors
docker-compose logs rag

# Check container details
docker inspect rag-product-search

# Try recreating
.\deploy.bat stop
docker-compose up -d
```

### Build Errors

```powershell
# Clean build (no cache)
docker build --no-cache -t rag-product-search:latest .

# Remove old images
docker rmi rag-product-search:latest
.\deploy.bat build
```

### Permission Issues

```powershell
# Run PowerShell as Administrator

# Or check Docker Desktop settings:
# Settings > Resources > File Sharing
# Ensure C:\ drive is shared
```

### Container Keeps Restarting

```powershell
# Check health
docker inspect --format='{{.State.Health}}' rag-product-search

# View crash logs
docker-compose logs --tail=100 rag
```

### Reset Everything

```powershell
# Stop and remove container
.\deploy.bat stop
docker-compose down

# Remove image
docker rmi rag-product-search:latest

# Clear database (WARNING: deletes indexed data)
Remove-Item -Recurse -Force database\chroma_db\*

# Rebuild and restart
.\deploy.bat build
.\deploy.bat start
.\deploy.bat index
```

---

## 📊 Expected Resource Usage

Monitor resources:
```powershell
docker stats rag-product-search
```

**Normal usage:**
- **Memory:** 2-4 GB
- **CPU:** 10-20% idle, up to 100% during queries
- **Disk:** ~3-5 GB total

---

## ✅ Success Checklist

Run these to verify everything works:

```powershell
# 1. Image built
docker images | findstr rag-product-search
# ✅ Should show rag-product-search image

# 2. Container running
docker ps | findstr rag-product-search
# ✅ Should show container with "Up" status

# 3. Data indexed
dir database\chroma_db
# ✅ Should show ChromaDB files

# 4. Stock reader works
.\deploy.bat test
# ✅ Should pass all tests

# 5. Collections loaded
docker-compose exec rag python -c "from src.core.retriever import UnifiedRetriever; r = UnifiedRetriever(); print(f'✓ OK')"
# ✅ Should print ✓ OK without errors
```

---

## 🚀 Ready for Server Deployment?

If all tests pass, you're ready to deploy to server!

**Transfer to server:**

```powershell
# Option 1: Using Git (recommended)
# Push to Git repository, then pull on server

# Option 2: Using SCP
scp -r C:\Users\adi\PycharmProjects\nlp user@server:/path/to/deployment/

# Option 3: Save image as tar
docker save rag-product-search:latest | gzip > rag-image.tar.gz
# Transfer rag-image.tar.gz to server
# On server: docker load < rag-image.tar.gz
```

---

## 📱 Common Commands Reference

```powershell
# Start
.\deploy.bat start

# Stop
.\deploy.bat stop

# Restart
.\deploy.bat restart

# Logs
.\deploy.bat logs

# Status
.\deploy.bat status

# Shell access
.\deploy.bat shell

# Test
.\deploy.bat test

# Demo
.\deploy.bat demo

# Index data
.\deploy.bat index

# Clean up
.\deploy.bat clean
```

---

## 📚 Next Steps

1. ✅ Complete all verification steps above
2. ✅ Ensure all tests pass
3. ✅ Document any issues
4. 🚀 Deploy to server using same commands
5. 🎉 Your RAG system is containerized!

---

**Need Help?**
- Review: [DOCKER.md](DOCKER.md) - Complete Docker guide
- Review: [DOCKER_TEST.md](DOCKER_TEST.md) - Detailed testing guide
- Check logs: `.\deploy.bat logs`
