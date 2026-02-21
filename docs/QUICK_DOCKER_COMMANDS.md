# Quick Docker Commands Reference

## 🚀 Quick Start

```bash
# Start the system
docker-compose up -d

# View logs
docker logs rag-product-search -f

# Stop the system
docker-compose down
```

## 📝 Running Scripts in Docker

### Main Query Interface (Interactive)
```bash
# Method 1: Using docker exec
docker exec -it rag-product-search python scripts/run_query.py

# Method 2: Access container shell first
docker exec -it rag-product-search bash
python scripts/run_query.py
```

### Verify System
```bash
# Check all collections
docker exec rag-product-search python scripts/testing/verify_collections.py

# Test retrieval
docker exec rag-product-search python -c "
import load_docker_compat
from src.core.retriever import UnifiedRetriever
r = UnifiedRetriever()
print(f'Products: {r.product_collection.count()}')
print(f'FAQs: {r.faq_collection.count()}')
print(f'Intents: {r.intent_collection.count()}')
"
```

### Indexing Data
```bash
# Index products
docker exec rag-product-search python scripts/indexing/index_products.py

# Parse and index intents
docker exec rag-product-search python scripts/indexing/parse_intent_data.py
docker exec rag-product-search python scripts/indexing/index_intent.py

# Index FAQs (requires ClickHouse)
docker exec rag-product-search python scripts/indexing/index_faq.py
```

### Windows Helper Scripts

From Windows Command Prompt or PowerShell:

```batch
REM Full setup (indexing)
scripts\windows\docker-setup-index.bat

REM Quick start (interactive)
scripts\windows\docker-run-interactive.bat

REM Rebuild container
scripts\windows\docker-rebuild.bat
```

## 🔍 Troubleshooting

### Check Container Status
```bash
docker ps
docker logs rag-product-search --tail 50
```

### Test if Scripts Work
```bash
# Should NOT show onnxruntime error
docker exec rag-product-search python scripts/run_query.py --help

# Should show "System ready!"
docker logs rag-product-search --tail 5
```

### Rebuild if Needed
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## 📊 Common Commands

| Task | Command |
|------|---------|
| **Start system** | `docker-compose up -d` |
| **Stop system** | `docker-compose down` |
| **View logs** | `docker logs rag-product-search -f` |
| **Run query** | `docker exec -it rag-product-search python scripts/run_query.py` |
| **Verify system** | `docker exec rag-product-search python scripts/testing/verify_collections.py` |
| **Access shell** | `docker exec -it rag-product-search bash` |
| **Rebuild** | `docker-compose build` |

## ✨ New Features (v2.1.1)

✅ All scripts now work directly in Docker
✅ No more onnxruntime errors
✅ Consistent behavior (Docker & local)
✅ Easier to run and test

---

**Status**: Ready after build completes
**Build Time**: ~30-45 min (first time)
**Documentation**: See `docs/docker/SCRIPT_FIX.md`
