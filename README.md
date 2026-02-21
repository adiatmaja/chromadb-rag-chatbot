# ChromaDB RAG Chatbot

A **Retrieval-Augmented Generation (RAG)** system for B2B e-commerce that combines semantic
search, vector databases, and LLM integration to provide intelligent customer service in
Indonesian language.

Built as part of R&D work at Sigma Solusi Indonesia.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5.0-green.svg)](https://www.trychroma.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## Overview

This system serves as the foundational chatbot layer for a B2B FMCG platform, enabling
semantic product search across colloquial Indonesian and Javanese product names, FAQ retrieval,
and 18+ e-commerce intent classification — all unified through a single retrieval interface
backed by ChromaDB.

---

## Architecture

```
  ┌──────────────────────────────────────────────────────────┐
  │  User Query (Indonesian / Javanese colloquial)           │
  └──────────────────────────┬───────────────────────────────┘
                             │
  ┌──────────────────────────▼───────────────────────────────┐
  │  Unified Retriever  (src/core/retriever.py)              │
  │  paraphrase-multilingual-MiniLM-L12-v2 → embeddings     │
  │  Parallel search across 3 ChromaDB collections          │
  └──────────┬─────────────────┬──────────────┬─────────────┘
             │                 │              │
             ▼                 ▼              ▼
       [Products]          [FAQs]        [Intents]
       11+ SKUs           15+ entries    18+ types
       colloquial         CSV / CH       e-commerce
       name mapping       sourced        actions
             │                 │              │
             └────────┬────────┴──────────────┘
                      │  best match by relevance_score
                      ▼
  ┌───────────────────────────────────────────────────────────┐
  │  UnifiedRAGOrchestrator  (src/core/orchestrator.py)      │
  │                                                           │
  │  if PRODUCT match:                                        │
  │    get_product_candidates(query, n=3)                     │
  │    → numbered list of candidates sent to LLM             │
  │    → LLM selects most relevant product (reranking)       │
  │                                                           │
  │  if explicit quantity:                                    │
  │    check_inventory(sku, qty)  ← function calling         │
  │    StockReader reads data/stock_data.csv                 │
  │    OrderTracker saves to database/orders.json            │
  │                                                           │
  │  OpenAI-compatible API (LM Studio / any provider)        │
  └──────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              Final response in Indonesian
```

---

## Features

- **Semantic Product Search** — understands colloquial and regional product names (e.g. "indomie kuning" → Indomie Mi Instan Rasa Ayam Bawang)
- **LLM Reranking** — top 3 product candidates sent to LLM for selection, avoiding embedding model precision issues between similar products
- **Intent Classification** — 18+ e-commerce intent types (cart ops, checkout, product inquiry, greetings)
- **FAQ Retrieval** — vectorized FAQ queried semantically; supports ClickHouse (production) or CSV (demo)
- **Unified Search** — single interface across all three knowledge bases, returns best match
- **LLM Integration** — works with any OpenAI-compatible API (LM Studio, OpenAI, Ollama)
- **Function Calling** — automatic inventory check via `check_inventory(sku, qty)` when user states a quantity
- **Order Tracking** — automatic order capture with persistent JSON storage
- **Docker-ready** — full Docker + Docker Compose deployment, no Python on host required
- **Windows-compatible** — UTF-8 encoding fixes and onnxruntime mock included

---

## Project Structure

```
chromadb-rag-chatbot/
├── src/
│   ├── core/
│   │   ├── retriever.py         # UnifiedRetriever — parallel search + get_product_candidates()
│   │   ├── orchestrator.py      # UnifiedRAGOrchestrator — reranking, LLM, function calling
│   │   └── order_tracker.py     # Persistent order tracking
│   ├── utils/
│   │   ├── clickhouse_client.py # ClickHouse FAQ data fetcher (production)
│   │   └── stock_reader.py      # CSV-based stock level reader
│   └── config.py                # Centralized config from .env
│
├── scripts/
│   ├── indexing/                # One-time data indexing scripts
│   │   ├── index_products.py    # product_data.csv → ChromaDB
│   │   ├── index_intent.py      # intent_data.csv → ChromaDB
│   │   ├── index_faq_csv.py     # faq_data.csv → ChromaDB (no-ClickHouse)
│   │   ├── index_faq.py         # ClickHouse FAQ → ChromaDB (production)
│   │   ├── parse_intent_data.py # intent.txt → intent_data.csv
│   │   └── verify_collections.py
│   └── run_query.py             # Interactive query interface (requires TTY)
│
├── data/                        # Sample data (replace with your own)
│   ├── product_data.csv         # Product catalog with pre-computed embedding_text
│   ├── stock_data.csv           # Inventory by warehouse (multi-warehouse schema)
│   ├── faq_data.csv             # FAQ entries for demo mode
│   └── intent.txt               # Intent definitions + examples
│
├── database/                    # ChromaDB + order storage (git-ignored)
├── deployment/                  # Docker deployment guides and helper scripts
├── docs/                        # Extended documentation
├── tests/                       # Integration tests (require live API server)
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/adiatmaja/chromadb-rag-chatbot
cd chromadb-rag-chatbot

# Configure environment
cp .env.example .env
# Edit .env: set LLM_BASE_URL and LLM_MODEL_NAME to match your LM Studio

# Build and run
docker-compose up -d

# First-time: index all data
docker-compose exec rag python scripts/indexing/parse_intent_data.py
docker-compose exec rag python scripts/indexing/index_intent.py
docker-compose exec rag python scripts/indexing/index_products.py
docker-compose exec rag python scripts/indexing/index_faq_csv.py

# Start interactive session (requires -it for TTY)
docker-compose exec -it rag python scripts/run_query.py
```

### Local Development

```bash
# Python 3.9+ required
pip install -r requirements.txt

# Windows only — install after requirements.txt
pip install onnxruntime==1.16.3

cp .env.example .env
# Edit .env with your LLM and embedding settings

# Index data
python scripts/indexing/parse_intent_data.py
python scripts/indexing/index_intent.py
python scripts/indexing/index_products.py
python scripts/indexing/index_faq_csv.py

# Run interactive query interface
python scripts/run_query.py
```

---

## Configuration

All configuration lives in `.env` (copy from `.env.example`):

```env
# LLM — any OpenAI-compatible endpoint
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL_NAME=qwen2.5-7b-instruct
LLM_API_KEY=lm-studio

# Embeddings — multilingual model required for Indonesian/Javanese
EMBEDDING_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2

# ChromaDB
VECTOR_DB_PATH=database/chroma_db
COLLECTION_NAME=fmcg_products
RETRIEVAL_TOP_K=1

# ClickHouse (optional, for production FAQ indexing)
CLICKHOUSE_HOST=your-host
CLICKHOUSE_PORT=8123
CLICKHOUSE_DB_NAME=your_database
```

Changing `EMBEDDING_MODEL_NAME` requires re-running all indexing scripts.

---

## Usage Examples

```python
from src.core.retriever import UnifiedRetriever

retriever = UnifiedRetriever()

# Semantic product search — returns top candidate by embedding score
result = retriever.search("indomie goreng")
print(f"Product: {result.metadata['official_name']}")
print(f"SKU: {result.metadata['sku']}")
print(f"Confidence: {result.relevance_score:.2%}")

# Get top 3 product candidates for LLM reranking
candidates = retriever.get_product_candidates("indomie goreng", n=3)
for c in candidates:
    print(f"  {c.metadata['sku']}: {c.metadata['official_name']} ({c.relevance_score:.2%})")

# Full RAG pipeline with reranking + function calling
from src.core.orchestrator import UnifiedRAGOrchestrator

orchestrator = UnifiedRAGOrchestrator(enable_order_tracking=True)
response = orchestrator.process_query("mau beli indomie goreng 2 dus")
print(response)
```

---

## Key Design Decisions

**LLM reranking for product disambiguation** — Embedding similarity alone cannot reliably
distinguish similar products (e.g. "indomie goreng" vs "indomie ayam bawang"). The retriever
fetches the top 3 candidates and the LLM selects the correct one from a numbered list. This
costs one extra embedding call per product query.

**Cosine distance required** — All ChromaDB collections must be created with
`metadata={"hnsw:space": "cosine"}`. The default L2 metric produces distances > 1,
which makes `relevance_score = 1 - distance` always clamp to 0.

**Pinned dependency versions** — `chromadb==0.5.0` is required (1.3.4 causes segfaults on
Windows with torch 2.8.0). `sentence-transformers==2.7.0` for the same reason.

**Hardcoded collection names** — `faq_collection` and `intent_collection` are constants in
`retriever.py`, not env vars. Only the product collection name is configurable via `COLLECTION_NAME`.

**CSV-based stock reading** — No live database connection at query time; `StockReader` reads
`data/stock_data.csv` directly, supporting multiple rows per SKU for multi-warehouse inventory.
`src/api/inventory_api.py` is a legacy FastAPI module kept for reference only.

---

## Performance

| Metric | Value |
|--------|-------|
| Embedding model | paraphrase-multilingual-MiniLM-L12-v2 (384 dimensions) |
| Languages supported | Indonesian, Javanese, + 50 other languages |
| Total indexed items | 44+ (products + FAQs + intents) |
| Memory footprint | ~500MB with model loaded |
| ChromaDB storage | ~2MB for full index |

---

## Troubleshooting

**All relevance scores are 0.0000** — Collections were indexed without `hnsw:space: cosine`. Re-run all indexing scripts (they delete and recreate collections).

**ChromaDB segfault on Windows** — Use `chromadb==0.5.0`, not 1.3.4.

**onnxruntime DLL error (Windows)** — Install `onnxruntime==1.16.3` after `requirements.txt` (excluded for Docker compatibility).

**Import errors** — Always run scripts from the project root, not from inside `scripts/`.

**LLM connection refused** — Start your LLM server first and verify `LLM_BASE_URL` in `.env`.

**`run_query.py` hangs or EOFError** — Requires an interactive TTY. Use `docker-compose exec -it rag python scripts/run_query.py`, not without `-it`.

**Script changes not reflected in Docker** — `src/` and `scripts/` are baked into the image. Run `docker-compose build && docker-compose up -d` after changes.

---

## Documentation

- [`deployment/DOCKER.md`](deployment/DOCKER.md) — Full Docker deployment guide
- [`docs/plans/`](docs/plans/) — Implementation plan history

---

## Acknowledgments

- [ChromaDB](https://www.trychroma.com/) — Vector database
- [sentence-transformers](https://www.sbert.net/) — Semantic embedding models
- [Rich](https://rich.readthedocs.io/) — Terminal UI

---

**Version**: 1.1.0 | **Status**: Production-ready
