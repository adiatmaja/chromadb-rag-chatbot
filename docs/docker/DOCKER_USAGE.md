# Docker Workflow Usage Guide

## Quick Start

### Option 1: Interactive Mode (Recommended for Testing)
Run the interactive query system where you can type queries:

```bash
# From your terminal (PowerShell/CMD)
docker-compose up
```

This will show you the interactive prompt where you can type queries directly.

### Option 2: Run in Background
Start container in background and execute commands:

```bash
# Start container
docker-compose up -d

# View logs
docker logs rag-product-search -f

# Stop container when done
docker-compose down
```

### Option 3: Using the Helper Script (Windows)
Double-click or run:

```bash
.\docker-run-interactive.bat
```

## Testing Queries

Once the container is running, you can test queries:

### Test with Python Script Inside Container
```bash
# Product search
docker exec rag-product-search python -c "
import sys
sys.path.insert(0, '/app/scripts')
from mock_onnxruntime import *
from src.core.retriever import UnifiedRetriever

retriever = UnifiedRetriever()
result = retriever.search('indomie goreng')
print(f'Found: {result.metadata}')
"

# FAQ search
docker exec rag-product-search python -c "
import sys
sys.path.insert(0, '/app/scripts')
from mock_onnxruntime import *
from src.core.retriever import UnifiedRetriever

retriever = UnifiedRetriever()
result = retriever.search('bagaimana cara pembayaran')
print(f'Type: {result.content_type.value}')
"

# Intent search
docker exec rag-product-search python -c "
import sys
sys.path.insert(0, '/app/scripts')
from mock_onnxruntime import *
from src.core.retriever import UnifiedRetriever

retriever = UnifiedRetriever()
result = retriever.search('checkout sekarang')
print(f'Type: {result.content_type.value}')
"
```

### Access Container Shell
```powershell
# From PowerShell or CMD
docker exec -it rag-product-search bash

# Inside container, run:
python scripts/docker_run_query.py
```

## Sample Test Queries

Once in the interactive system, try:

### Product Queries:
- `cari indomie goreng`
- `ada minyak goreng ga?`
- `saya mau beli teh kotak`
- `mie ayam 10 dus` (with quantity for stock check)

### FAQ Queries:
- `bagaimana cara pembayaran?`
- `berapa lama pengiriman?`
- `apakah bisa COD?`

### Intent Queries:
- `checkout sekarang`
- `tambah ke keranjang`
- `lihat profil saya`
- `batalkan pesanan`

## System Commands

Inside the interactive system:
- `help` - Show available commands
- `stats` - Show collection statistics
- `orders` - View tracked orders
- `clear` - Clear screen
- `quit` or `exit` - Exit system

## Troubleshooting

### Container not starting?
```bash
# Check Docker status
docker ps -a

# View container logs
docker logs rag-product-search

# Rebuild if needed
docker-compose up --build
```

### Reset everything
```bash
# Stop and remove containers
docker-compose down

# Remove volumes (careful: deletes data)
docker-compose down -v

# Rebuild from scratch
docker-compose up --build
```

### Check system health
```bash
# Check if container is healthy
docker ps

# Verify collections
docker exec rag-product-search python -c "
import sys
sys.path.insert(0, '/app/scripts')
from mock_onnxruntime import *
from src.core.retriever import UnifiedRetriever
r = UnifiedRetriever()
print(f'Products: {r.product_collection.count()}')
print(f'FAQs: {r.faq_collection.count()}')
print(f'Intents: {r.intent_collection.count()}')
"
```

## Current Status

✅ Container: `rag-product-search` is running
✅ Collections loaded:
  - 11 products
  - 29 FAQs
  - 35 intents
✅ LLM connected: https://pcllm.sigmasolusi.com/v1
✅ Stock data: 30 entries
✅ Order tracker: 9 existing orders

## Next Steps

1. **Test the workflow**: Run `docker-compose up` and try sample queries
2. **Check documentation**: See `deployment/DOCKER.md` for advanced usage
3. **View logs**: Use `docker logs rag-product-search -f` to monitor
4. **Stop when done**: Press Ctrl+C or run `docker-compose down`
