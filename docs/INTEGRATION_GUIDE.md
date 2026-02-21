# Complete System Integration Guide

## 🎯 Overview

This guide walks you through setting up and running the complete RAG Product Search System with real inventory API integration.

---

## 📦 System Components

| Component | File | Purpose | Port |
|-----------|------|---------|------|
| **Vector Database** | `chroma_db/` | Product embeddings storage | - |
| **Inventory API** | `stock_api.py` | Real-time stock management | 8000 |
| **RAG System** | `llm_processor.py` | Query processing & LLM | - |
| **LM Studio** | External | Local LLM server | 1234 |

---

## 🚀 Complete Setup (Step-by-Step)

### Step 1: Install Updated Dependencies

```bash
# Ensure you have the updated requirements.txt
pip install -r requirements.txt

# Verify FastAPI installation
python -c "import fastapi; print(f'FastAPI {fastapi.__version__} installed')"

# Verify requests library
python -c "import requests; print('Requests library ready')"
```

**Expected Output**:
```
FastAPI 0.104.x installed
Requests library ready
```

---

### Step 2: Prepare Data Files

Ensure these files exist in your project root:

```bash
# Check required files
ls -la product_data.csv stock_data.csv

# If stock_data.csv is missing, create it from the template provided
```

**product_data.csv**: Product master data (already exists)  
**stock_data.csv**: Inventory data (newly created)

---

### Step 3: Build Vector Database (if not done)

```bash
# This step is required before running the system
python index_data.py
```

**Expected Output**:
```
✅ Indexing Complete!
📊 Total products indexed: 10
```

---

### Step 4: Start the Inventory API

**Open Terminal 1:**

```bash
# Start the inventory API server
python stock_api.py
```

**Expected Output**:
```
======================================================================
  Product Inventory Management API
  Version: 1.0.0
======================================================================

Starting API server...
API Documentation: http://localhost:8000/docs
Alternative Docs: http://localhost:8000/redoc
Health Check: http://localhost:8000/health

Press CTRL+C to stop the server

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Verify API is Running:**

```bash
# In another terminal
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-11-10T10:30:00.123456",
  "total_products": 10,
  "total_warehouses": 3
}
```

---

### Step 5: Start LM Studio (if using full RAG)

1. **Open LM Studio**
2. **Load a Model** (e.g., `gemma-2b-it`, `llama-2-7b-chat`)
3. **Start Local Server**:
   - Click "Local Server" tab
   - Click "Start Server"
   - Default: http://localhost:1234

**Verify LM Studio:**

```bash
curl http://localhost:1234/v1/models
```

---

### Step 6: Test the Complete System

**Open Terminal 2 (while API is running in Terminal 1):**

```bash
# Run the complete RAG pipeline with real API
python llm_processor.py
```

**Expected Output**:
```
======================================================================
      RAG System - Complete Pipeline Test (Real API)      
======================================================================

🤖 Initializing RAG Orchestrator...
Setting up product retriever...
✅ Connected to collection 'fmcg_products' with 10 products
Connecting to LLM: http://localhost:1234/v1
Model: gemma-2b-it
Connecting to Inventory API: http://localhost:8000
✅ Inventory API connection verified
✅ RAG Orchestrator ready!

═══════════════════════════════════════════════════════════════════
Scenario 1: Small Order (Should Have Stock)
Expected: Should trigger check_inventory and confirm availability
═══════════════════════════════════════════════════════════════════

======================================================================
Processing Query: Mau beli 2 dus Indomie kuning
======================================================================

Step 1: Retrieval from Vector Database
🔍 User Query: Mau beli 2 dus Indomie kuning
Processing query...

✅ Product Found (Retrieval Complete):
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field              ┃ Value                                      ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ SKU Kanonis        │ IR001                                      │
│ Nama Resmi         │ Indomie Mi Instan Rasa Kaldu Ayam         │
│ Kuantitas Dus      │ 1 dus = 40 pcs                            │
│ Sinonim Dikenal    │ Indomie Rebus; Indomie Kuning; Mie Soto   │
└────────────────────┴────────────────────────────────────────────┘

Step 2: Building Context for LLM
Context: SKU: IR001, Nama Resmi: Indomie Mi Instan Rasa Kaldu Ayam...

Step 3: LLM Inference
⏳ Waiting for LLM response...
🔧 Function calling detected!
Function: check_inventory
Arguments: {
  "sku": "IR001",
  "requested_quantity": 80
}

📡 Calling Inventory API: http://localhost:8000/api/v1/inventory/check
Payload: {
  "sku": "IR001",
  "requested_quantity": 80
}
✅ Inventory API response received
Response: {
  "status": "success",
  "available": true,
  "sku": "IR001",
  "requested_quantity": 80,
  "available_quantity": 890,
  "warehouse": "Gudang A",
  "message": "Stok IR001 sebanyak 80 pcs tersedia di Gudang A..."
}

⏳ Generating final response...
✅ Final response generated

📝 Final Response:
╭────────────────── LLM Response ──────────────────╮
│                                                  │
│  Baik, pesanan Anda untuk Indomie Mi Instan     │
│  Rasa Kaldu Ayam (SKU IR001) sebanyak 2 dus     │
│  (80 pcs) tersedia di Gudang A. Silakan         │
│  lanjutkan proses pembayaran.                   │
│                                                  │
╰──────────────────────────────────────────────────╯
```

---

## 🔄 Complete System Workflow

### Visual Flow Diagram

```
User: "Mau beli 2 dus Indomie kuning"
    ↓
┌─────────────────────────────────────┐
│ 1. RETRIEVAL (search_agent.py)     │
│    - Convert query to embedding     │
│    - Search ChromaDB                │
│    - Return: SKU IR001 matched      │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ 2. CONTEXT BUILDING                 │
│    - Format product metadata        │
│    - Create system prompt           │
│    - Prepare for LLM                │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ 3. LLM INFERENCE (LM Studio)        │
│    - Analyze query + context        │
│    - Detect: need inventory check   │
│    - Generate function call:        │
│      check_inventory(IR001, 80)     │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ 4. INVENTORY API CALL               │
│    POST /api/v1/inventory/check     │
│    {                                │
│      "sku": "IR001",                │
│      "requested_quantity": 80       │
│    }                                │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ 5. INVENTORY MANAGER                │
│    - Query stock_data.csv           │
│    - Calculate availability         │
│    - Return: 890 pcs available      │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ 6. API RESPONSE                     │
│    {                                │
│      "status": "success",           │
│      "available": true,             │
│      "available_quantity": 890,     │
│      "warehouse": "Gudang A"        │
│    }                                │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ 7. FINAL LLM GENERATION             │
│    - Receive API response           │
│    - Generate natural language      │
│    - Format user-friendly message   │
└────────────┬────────────────────────┘
             ↓
User receives: "Baik, pesanan Anda untuk 
Indomie Mi Instan Rasa Kaldu Ayam (SKU 
IR001) sebanyak 2 dus (80 pcs) tersedia 
di Gudang A. Silakan lanjutkan proses 
pembayaran."
```

---

## 🧪 Testing Scenarios

### Scenario 1: Small Order (Available Stock)

**Query**: "Mau beli 2 dus Indomie kuning"

**Expected**:
- ✅ Retrieves IR001
- ✅ Calculates 2 dus = 80 pcs
- ✅ Calls inventory API
- ✅ API confirms availability (890 pcs available)
- ✅ LLM generates success message

---

### Scenario 2: Large Order (Partial Stock)

**Query**: "Saya butuh 20 dus minyak Bimoli 2L"

**Expected**:
- ✅ Retrieves MS010
- ✅ Calculates 20 dus × 6 pouch = 120 pouch (assuming 1 dus = 6)
- ✅ Calls inventory API
- ✅ API returns partial availability
- ✅ LLM suggests available quantity

---

### Scenario 3: Product Inquiry (No Quantity)

**Query**: "tolong carikan SKM kaleng"

**Expected**:
- ✅ Retrieves SR003
- ✅ No quantity mentioned
- ✅ No inventory API call
- ✅ LLM provides product information

---

### Scenario 4: Unknown Product

**Query**: "Ada rokok Marlboro?"

**Expected**:
- ✅ No product match in vector DB
- ✅ Returns "product not found" message
- ✅ No API call made

---

## 🔍 Monitoring & Debugging

### Check API Logs

While API is running, you'll see request logs:

```
INFO:     127.0.0.1:54321 - "POST /api/v1/inventory/check HTTP/1.1" 200 OK
INFO:     Request: {"sku": "IR001", "requested_quantity": 80}
INFO:     Response: {"status": "success", ...}
```

### Interactive API Testing

Open http://localhost:8000/docs in browser:

1. **Try the "Check Stock Availability" endpoint**:
   - Click "Try it out"
   - Enter SKU: `IR001`
   - Enter quantity: `80`
   - Click "Execute"
   - View real-time response

### Check System Health

```bash
# Check API
curl http://localhost:8000/health

# Check LM Studio
curl http://localhost:1234/v1/models

# Check Vector DB
python -c "from search_agent import ProductRetriever; r = ProductRetriever(); print('Vector DB OK')"
```

---

## 🛠️ Troubleshooting Integration Issues

### Issue 1: API Connection Error

**Error**: `ConnectionError: Inventory API not accessible`

**Checklist**:
```bash
# 1. Is API running?
curl http://localhost:8000/health

# 2. Check the port
netstat -an | grep 8000

# 3. Restart API
python stock_api.py
```

---

### Issue 2: Function Not Being Called

**Symptom**: LLM doesn't call check_inventory even with quantity

**Solutions**:
1. **Check LLM Model**: Ensure it supports function calling
2. **Verify Temperature**: Set to 0.0 in `.env`
3. **Check System Prompt**: Should mention function availability
4. **Try Different Query**: "Saya mau pesan 3 dus Indomie"

---

### Issue 3: Wrong Quantity Calculation

**Symptom**: LLM calculates wrong quantity conversion

**Solutions**:
1. **Improve Context**: Add unit conversion info to embedding_text
2. **Update System Prompt**: Add conversion rules
3. **Check pack_size_desc**: Ensure clear format (e.g., "1 dus = 40 pcs")

---

### Issue 4: Slow Response

**Symptom**: Takes >10 seconds for response

**Solutions**:
1. **Check LLM**: Larger models = slower inference
2. **Monitor API**: Should respond in <100ms
3. **Check Network**: Ensure localhost connections
4. **Review Logs**: Look for bottlenecks

---

## 📊 Performance Monitoring

### Expected Response Times

| Step | Expected Time | Notes |
|------|---------------|-------|
| Vector Search | 10-50ms | ChromaDB query |
| API Call | 50-100ms | Stock check |
| LLM Inference | 500-2000ms | Model dependent |
| Total Pipeline | 1-3 seconds | End-to-end |

### Optimization Tips

1. **Use Faster Model**: gemma-2b-it < llama-7b < llama-13b
2. **Enable Caching**: Cache frequent queries
3. **Batch Requests**: Process multiple queries together
4. **Use GPU**: Enable GPU for sentence-transformers

---

## 🔧 Advanced Configuration

### Custom API URL

If running API on different machine:

```python
# In llm_processor.py, update:
INVENTORY_API_BASE_URL = "http://192.168.1.100:8000"
```

### Multiple Warehouses

To prefer specific warehouse:

```python
# Modify API call to include warehouse_id
inventory_client.check_inventory(
    sku="IR001",
    requested_quantity=80,
    warehouse_id="WH001"  # Specific warehouse
)
```

### Custom Timeout

```python
# In llm_processor.py
INVENTORY_API_TIMEOUT = 30  # Increase to 30 seconds
```

---

## 📝 Data Maintenance

### Updating Stock Levels

```bash
# Edit stock data
nano stock_data.csv

# Update quantity for IR001 in WH001
# IR001,Indomie...,WH001,Gudang A,...,600,100,100
#                                      ^^^
#                                    Update this

# Restart API to load changes
# CTRL+C in Terminal 1, then
python stock_api.py
```

### Adding New Products

1. **Add to product_data.csv**:
```csv
NEW01,New Product Name,"Alias1; Alias2",1 dus = 50 pcs,"Embedding text..."
```

2. **Add to stock_data.csv**:
```csv
NEW01,New Product Name,WH001,Gudang A,Jakarta,500,50,100
NEW01,New Product Name,WH002,Gudang B,Bekasi,300,30,100
```

3. **Rebuild vector database**:
```bash
python index_data.py
```

4. **Restart API**:
```bash
# CTRL+C then
python stock_api.py
```

---

## 🎓 Best Practices

1. **Always Start API First**: Before running RAG system
2. **Monitor Logs**: Watch both terminals for errors
3. **Test Incrementally**: Test each component separately
4. **Keep Data Synced**: product_data.csv ↔ stock_data.csv
5. **Use Health Checks**: Verify systems before full test
6. **Document Changes**: Note any custom configurations
7. **Backup Data**: Keep backups of CSV files

---

## 📚 Quick Reference

### Start/Stop Commands

```bash
# Terminal 1: Start API
python stock_api.py
# Stop: CTRL+C

# Terminal 2: Run RAG System
python llm_processor.py

# Test Retrieval Only (no LLM)
python search_agent.py

# Rebuild Vector DB
python index_data.py

# Validate Configuration
python config.py
```

### Important URLs

- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health
- **LM Studio**: http://localhost:1234
- **LLM Models**: http://localhost:1234/v1/models

### File Locations

```
fmcg_rag_poc/
├── product_data.csv      # Product master (10 products)
├── stock_data.csv        # Inventory data (30 records)
├── chroma_db/           # Vector database
├── stock_api.py         # API server
├── llm_processor.py     # RAG orchestrator
├── search_agent.py      # Retrieval system
└── config.py            # Configuration
```

---

## 🎉 Success Checklist

Before considering setup complete, verify:

- [ ] ✅ Virtual environment activated
- [ ] ✅ All dependencies installed (including FastAPI)
- [ ] ✅ product_data.csv exists
- [ ] ✅ stock_data.csv exists
- [ ] ✅ Vector database built (chroma_db/ folder exists)
- [ ] ✅ API starts without errors
- [ ] ✅ API health check returns 200
- [ ] ✅ LM Studio running (if using full RAG)
- [ ] ✅ RAG system connects to API successfully
- [ ] ✅ Test scenario completes successfully
- [ ] ✅ Real inventory data returned from API

---

## 🆘 Need Help?

If you're stuck:

1. **Review this guide** from the beginning
2. **Check logs** in both terminals for error messages
3. **Test components individually**:
   - API only: `python stock_api.py` → `curl http://localhost:8000/health`
   - Retrieval only: `python search_agent.py`
   - Full system: `python llm_processor.py`
4. **Verify data files** are correctly formatted
5. **Check firewall/antivirus** not blocking ports

---

**You're now ready to use the complete RAG system with real inventory API integration! 🚀**