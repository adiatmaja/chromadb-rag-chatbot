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
semantic product search across colloquial Indonesian and Javanese product names, FAQ retrieval
from a ClickHouse database, and 35+ e-commerce intent classification — all unified through a
single retrieval interface backed by ChromaDB.

---

## Architecture

```
  ┌──────────────────────────────────────────────────────────┐
  │  User Query (Indonesian / Javanese colloquial)           │
  └──────────────────────────┬───────────────────────────────┘
                             │
  ┌──────────────────────────▼───────────────────────────────┐
  │  Unified Retriever                                       │
  │  sentence-transformers (all-MiniLM-L6-v2) → embeddings  │
  │  Parallel search across 3 ChromaDB collections          │
  └──────────┬─────────────────┬──────────────┬─────────────┘
             │                 │              │
             ▼                 ▼              ▼
       [Products]          [FAQs]        [Intents]
       11+ SKUs           29+ entries    35 types
       colloquial         ClickHouse     e-commerce
       name mapping       sourced        actions
             │                 │              │
             └────────┬────────┴──────────────┘
                      │  best match by relevance_score
                      ▼
  ┌───────────────────────────────────────────────────────────┐
  │  UnifiedRAGOrchestrator                                   │
  │  • Context-aware LLM prompt building                     │
  │  • OpenAI-compatible API (LM Studio / any provider)      │
  │  • Function calling: check_inventory(sku, qty)           │
  └───────────────────────────────────────────────────────────┘
                      │
                      ▼
  ┌───────────────────────────────────────────────────────────┐
  │  Response + Order Tracking                               │
  │  • StockReader (CSV-based inventory check)               │
  │  • OrderTracker (persistent JSON storage)                │
  └───────────────────────────────────────────────────────────┘
```

---

## Features

- **Semantic Product Search** — understands colloquial and regional product names (e.g. "indomie kuning" → Noodle Instant Original)
- **Intent Classification** — 35+ e-commerce intent types (cart ops, checkout, product inquiry, greetings)
- **FAQ Retrieval** — vectorized FAQ from ClickHouse, queried semantically
- **Unified Search** — single interface across all three knowledge bases, returns best match
- **LLM Integration** — works with any OpenAI-compatible API (LM Studio, OpenAI, Ollama)
- **Order Tracking** — automatic order capture via LLM function calling, persistent JSON storage
- **Docker-ready** — full Docker + Docker Compose deployment, no Python on host required
- **Windows-compatible** — UTF-8 encoding fixes included throughout

---

## Project Structure

```
chromadb-rag-chatbot/
├── src/
│   ├── core/
│   │   ├── retriever.py         # UnifiedRetriever — parallel search across collections
│   │   ├── orchestrator.py      # UnifiedRAGOrchestrator — LLM context + function calling
│   │   └── order_tracker.py     # Persistent order tracking
│   ├── utils/
│   │   ├── clickhouse_client.py # ClickHouse FAQ data fetcher
│   │   └── stock_reader.py      # CSV-based stock level reader
│   └── config.py                # Centralized config from .env
│
├── scripts/
│   ├── indexing/                # One-time data indexing scripts
│   │   ├── index_products.py    # Product CSV → ChromaDB
│   │   ├── index_intent.py      # Intent CSV → ChromaDB
│   │   ├── index_faq.py         # ClickHouse FAQ → ChromaDB
│   │   └── parse_intent_data.py # intent.txt → intent_data.csv
│   ├── testing/                 # Verification scripts
│   ├── demo/                    # Full workflow demos
│   └── run_query.py             # Interactive query interface
│
├── data/                        # Sample data (replace with your own)
│   ├── product_data.csv         # Product catalog
│   ├── stock_data.csv           # Inventory stock levels
│   └── intent.txt               # Intent definitions + examples
│
├── database/                    # ChromaDB persistent storage (git-ignored)
├── examples/                    # Usage examples
├── tests/                       # Unit tests
├── docs/                        # Extended documentation
├── deployment/                  # Docker deployment guides
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
# Edit .env with your LLM URL and ClickHouse credentials

# Build and run
docker-compose up -d

# First-time: index all data
docker-compose exec rag bash
python scripts/indexing/parse_intent_data.py
python scripts/indexing/index_intent.py
python scripts/indexing/index_products.py
exit
```

### Local Development

```bash
# Python 3.9+ required
pip install -r requirements.txt
cp .env.example .env

# Index data
python scripts/indexing/parse_intent_data.py
python scripts/indexing/index_intent.py
python scripts/indexing/index_products.py

# Run interactive query interface
python scripts/run_query.py
```

---

## Configuration

All configuration lives in `.env` (copy from `.env.example`):

```env
# LLM — any OpenAI-compatible endpoint
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL_NAME=your-model-name
LLM_API_KEY=lm-studio

# Embeddings
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# ChromaDB
VECTOR_DB_PATH=database/chroma_db
COLLECTION_NAME=fmcg_products
RETRIEVAL_TOP_K=1

# ClickHouse (optional, for FAQ indexing)
CLICKHOUSE_HOST=your-host
CLICKHOUSE_PORT=8123
CLICKHOUSE_DB_NAME=your_database
```

---

## Usage Examples

```python
from src.core.retriever import UnifiedRetriever

retriever = UnifiedRetriever()

# Semantic product search (handles colloquial names)
result = retriever.search("quick noodle original")
print(f"Product: {result.metadata['official_name']}")
print(f"SKU: {result.metadata['sku']}")
print(f"Confidence: {result.relevance_score:.2%}")

# Intent classification
result = retriever.search(
    "Checkout now",
    search_products=False,
    search_intents=True
)
print(f"Intent: {result.metadata['intent_name']}")

# Full RAG pipeline
from src.core.orchestrator import UnifiedRAGOrchestrator

orchestrator = UnifiedRAGOrchestrator(enable_order_tracking=True)
response = orchestrator.process_query("I want to order 3 boxes of noodles")
print(response)
```

---

## Key Design Decisions

**Pinned dependency versions** — ChromaDB 0.5.0 is required (1.3.4 causes segfaults on Windows
with torch 2.8.0). `sentence-transformers==2.7.0` for the same reason with torch 2.8.0.

**Hardcoded collection names** — FAQ and intent collection names (`faq_collection`,
`intent_collection`) are constants in `retriever.py`, not env vars, to keep config minimal.

**CSV-based stock reading** — No live database connection at query time; `StockReader` reads
`data/stock_data.csv` directly. This makes the system runnable without database access for
demos and development.

**Single best-match retrieval** — `RETRIEVAL_TOP_K=1` returns the single highest-confidence
result across all collections, keeping LLM context tight and reducing hallucination surface.

---

## Performance

| Metric | Value |
|--------|-------|
| Embedding model | all-MiniLM-L6-v2 (384 dimensions) |
| Total indexed items | 74+ (products + FAQs + intents) |
| Query latency | < 500ms (retrieval + LLM) |
| Memory footprint | ~500MB with model loaded |
| ChromaDB storage | ~2MB for full index |

---

## Documentation

- [`docs/INTENT_SYSTEM.md`](docs/INTENT_SYSTEM.md) — Full intent classification guide
- [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md) — API reference
- [`docs/FAQ_INTEGRATION.md`](docs/FAQ_INTEGRATION.md) — ClickHouse FAQ setup
- [`deployment/DOCKER.md`](deployment/DOCKER.md) — Full Docker deployment guide
- [`docs/QUICK_START.md`](docs/QUICK_START.md) — Condensed setup steps

---

## Troubleshooting

**ChromaDB segfault on Windows** — Use `chromadb==0.5.0`, not 1.3.4.

**onnxruntime DLL error (Windows)** — Install `onnxruntime==1.16.3` locally
(excluded from `requirements.txt` for Docker compatibility).

**Import errors** — Always run scripts from the project root, not from inside `scripts/`.

**LLM connection refused** — Start your LLM server first and verify `LLM_BASE_URL` in `.env`.

---

## Acknowledgments

- [ChromaDB](https://www.trychroma.com/) — Vector database
- [sentence-transformers](https://www.sbert.net/) — Semantic embedding models
- [Rich](https://rich.readthedocs.io/) — Terminal UI

---

**Version**: 1.0.0 | **Status**: Production-ready
