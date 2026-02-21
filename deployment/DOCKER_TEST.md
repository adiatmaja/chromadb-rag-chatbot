# Docker Testing Guide - Windows PC

Quick guide to test Docker setup on your Windows PC before deploying to server.

---

## ✅ Prerequisites Check

1. **Docker Desktop Running**: Ensure Docker Desktop is running (check system tray)
2. **WSL2 Backend**: Docker Desktop should be using WSL2 backend
3. **LM Studio Running** (optional): For full LLM testing

---

## 🧪 Step-by-Step Testing

### Step 1: Verify Docker Installation

Open PowerShell or Command Prompt and run:

```powershell
docker --version
docker-compose --version
```

Expected output:
```
Docker version 20.10.x or higher
Docker Compose version 2.x.x or higher
```

---

### Step 2: Build the Docker Image

```powershell
# Navigate to project directory
cd C:\Users\adi\PycharmProjects\nlp

# Build using helper script (recommended)
.\deploy.bat build

# OR build using docker directly
docker build -t rag-product-search:latest .
```

**Expected output:**
- Build progress with multiple steps
- Final message: "Successfully tagged rag-product-search:latest"
- Build time: ~5-10 minutes (first time)

**Verify image was created:**
```powershell
docker images | findstr rag-product-search
```

Should show:
```
rag-product-search    latest    <image-id>    <time>    <size>
```

---

### Step 3: Test Run the Container

```powershell
# Start container in detached mode
.\deploy.bat start

# OR using docker-compose directly
docker-compose up -d
```

**Verify container is running:**
```powershell
.\deploy.bat status

# OR
docker ps | findstr rag-product-search
```

Should show container running.

---

### Step 4: Check Container Logs

```powershell
# View logs
docker-compose logs rag

# OR follow logs in real-time
docker-compose logs -f rag
```

**Look for:**
- ✅ "Unified RAG Orchestrator ready!"
- ✅ "Stock data loaded (30 entries)"
- ✅ Collections loaded (products, FAQs, intents)
- ⚠️ Any error messages

---

### Step 5: Access Container Shell

```powershell
# Access bash shell inside container
.\deploy.bat shell

# OR
docker-compose exec rag bash
```

**Inside container, verify:**

```bash
# Check Python version
python --version

# Check project structure
ls -la

# Verify data files exist
ls -la data/
ls -la database/

# Test imports
python -c "from src.core.retriever import UnifiedRetriever; print('✓ Imports OK')"

# Exit shell
exit
```

---

### Step 6: Test Stock Reader

```powershell
# Test stock reader directly
.\deploy.bat test

# OR
docker-compose run --rm rag python -m src.utils.stock_reader
```

**Expected output:**
- ✅ Stock data loaded successfully
- ✅ Total rows: 30
- ✅ Multiple test cases passing
- Stock availability checks working

---

### Step 7: Index Data (First Time)

```powershell
# Index all data using helper script
.\deploy.bat index

# OR manually
docker-compose exec rag python scripts/indexing/parse_intent_data.py
docker-compose exec rag python scripts/indexing/index_intent.py
docker-compose exec rag python scripts/indexing/index_products.py
```

**Expected output:**
- ✅ Intent data parsed successfully
- ✅ 35 intents indexed to ChromaDB
- ✅ 11 products indexed to ChromaDB

**Verify indexes created:**
```powershell
# Check database directory
dir database\chroma_db

# Should see ChromaDB files
```

---

### Step 8: Run Demo Workflow

```powershell
# Run full workflow demo
.\deploy.bat demo

# OR
docker-compose run --rm rag python scripts/demo/demo_full_workflow.py
```

**Expected output:**
- System initialization messages
- 5 test queries processed
- Product search, FAQ, and intent results
- Order tracking summary

**⚠️ Note:** If LLM is not running, you'll see connection errors but retrieval should still work.

---

### Step 9: Test Retriever (Without LLM)

```powershell
docker-compose exec rag python scripts/testing/verify_collections.py
```

**Expected output:**
- ✅ Product collection: 11 products loaded
- ✅ FAQ collection: 29 FAQs loaded
- ✅ Intent collection: 35 intents loaded
- Test queries returning results

---

### Step 10: Test Full System (With LLM)

**Prerequisites:**
1. Start LM Studio on your PC
2. Load a model (e.g., gemma-2b-it)
3. Ensure server is running on port 1234

**Update .env:**
```env
LLM_BASE_URL=http://host.docker.internal:1234/v1
LLM_MODEL_NAME=your-model-name
```

**Restart container:**
```powershell
.\deploy.bat restart
```

**Run interactive query:**
```powershell
docker-compose run --rm rag python scripts/run_query.py
```

**Test queries:**
```
> Saya ingin pesan 2 dus indomie goreng
> Ada berapa pcs dalam 1 dus indomie?
> exit
```

---

## 🐛 Troubleshooting

### Container Won't Start

**Check logs:**
```powershell
docker-compose logs rag
```

**Common issues:**
- Missing .env file → Copy from .env.example
- Port conflicts → Check if another service is using ports
- Docker Desktop not running → Start Docker Desktop

### Build Fails

**Clean build:**
```powershell
docker-compose down
docker rmi rag-product-search:latest
docker build --no-cache -t rag-product-search:latest .
```

### Can't Access LLM from Container

**Test connectivity:**
```powershell
docker-compose exec rag curl http://host.docker.internal:1234/v1/models
```

**If fails:**
- Check LM Studio is running
- Verify firewall settings
- Try using your PC's IP instead of `host.docker.internal`

### Database Issues

**Reset database:**
```powershell
# Stop container
.\deploy.bat stop

# Remove database files
Remove-Item -Recurse -Force database\chroma_db\*

# Restart and re-index
.\deploy.bat start
.\deploy.bat index
```

### Permission Errors

**On Windows:**
- Run PowerShell as Administrator
- Ensure Docker Desktop has access to C: drive (Settings > Resources > File Sharing)

---

## ✅ Success Checklist

Before deploying to server, verify:

- [ ] Docker image builds successfully
- [ ] Container starts and runs
- [ ] Stock reader test passes
- [ ] Data indexing completes without errors
- [ ] Collections loaded (products, FAQs, intents)
- [ ] Retriever tests pass
- [ ] Demo workflow runs successfully
- [ ] Can access container shell
- [ ] Logs show no critical errors

---

## 🎯 Quick Test Commands

```powershell
# Complete test sequence
.\deploy.bat build
.\deploy.bat start
.\deploy.bat status
.\deploy.bat index
.\deploy.bat test
.\deploy.bat demo
.\deploy.bat logs

# Clean up when done testing
.\deploy.bat stop
```

---

## 📊 Expected Resource Usage

Monitor with:
```powershell
docker stats rag-product-search
```

**Typical usage:**
- CPU: 10-20% idle, up to 100% during queries
- Memory: 2-4 GB
- Disk: ~3-5 GB for image + data

---

## 🚀 Next Steps

If all tests pass:
1. ✅ Docker setup is working correctly
2. ✅ Ready to deploy to server
3. ✅ Transfer files to server using Git or SCP
4. ✅ Run same commands on server

---

**Need Help?**
- Check main [DOCKER.md](DOCKER.md) for detailed guide
- Review logs: `.\deploy.bat logs`
- Access shell: `.\deploy.bat shell`
