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
  │  LazarusNLP/all-indo-e5-small-v4 → embeddings           │
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
  │    get_product_candidates(query, n=5)                     │
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

- **Indonesian-specialist Embeddings** — uses `LazarusNLP/all-indo-e5-small-v4`, a fine-tuned E5 model optimised for Indonesian; embedding texts across all data files are pure Indonesian for maximum alignment
- **Semantic Product Search** — understands colloquial and regional product names (e.g. "indomie kuning" → Indomie Mi Instan Rasa Ayam Bawang)
- **LLM Reranking** — top 5 product candidates sent to LLM for selection, resolving embedding model precision issues between similar products
- **Intent Classification** — 18 e-commerce intent types (cart operations, checkout, product inquiry, greetings, and more)
- **FAQ Retrieval** — vectorized FAQ queried semantically; supports ClickHouse (production) or CSV (demo)
- **Unified Search** — single interface across all three knowledge bases, returns best match by cosine similarity
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
│   ├── run_query.py             # Interactive query interface (requires TTY)
│   └── testing/
│       └── test_all_retrieval.py  # Comprehensive retrieval test (44 cases)
│
├── data/                        # Sample data (replace with your own)
│   ├── product_data.csv         # Product catalog with pre-computed embedding_text
│   ├── stock_data.csv           # Inventory by warehouse (multi-warehouse schema)
│   ├── faq_data.csv             # FAQ entries for demo mode
│   ├── intent_data.csv          # Intent definitions with hand-tuned Indonesian embedding_text
│   └── intent.txt               # Raw intent source (do not regenerate intent_data.csv from this)
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
# (intent_data.csv is pre-configured — skip parse_intent_data.py)
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

# Index data (intent_data.csv is pre-configured — skip parse_intent_data.py)
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

# Embeddings — Indonesian-specialist E5 model (384-dim, ~120MB)
EMBEDDING_MODEL_NAME=LazarusNLP/all-indo-e5-small-v4

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

# Get top 5 product candidates for LLM reranking
candidates = retriever.get_product_candidates("indomie goreng", n=5)
for c in candidates:
    print(f"  {c.metadata['sku']}: {c.metadata['official_name']} ({c.relevance_score:.2%})")

# Full RAG pipeline with reranking + function calling
from src.core.orchestrator import UnifiedRAGOrchestrator

orchestrator = UnifiedRAGOrchestrator(enable_order_tracking=True)
response = orchestrator.process_query("mau beli indomie goreng 2 dus")
print(response)
```

---

## Retrieval Test

A comprehensive test covers all 11 products, 15 FAQs, and 18 intents.

```bash
PYTHONIOENCODING=utf-8 docker exec rag-product-search \
  python scripts/testing/test_all_retrieval.py
```

**Sample output:**

```
══════════════════════════════════════════════════════════════════════
  COMPREHENSIVE RETRIEVAL TEST
  Products=11  FAQs=15  Intents=18
══════════════════════════════════════════════════════════════════════

══════════════════════════════════════════════════════════════════════
  PRODUCT RETRIEVAL  (target SKU must appear in top-5 candidates)
══════════════════════════════════════════════════════════════════════
  [PASS]  Indomie Mi Goreng Original             query='indomie goreng'          rank #1  top_score=0.646
  [PASS]  Indomie Mi Instan Ayam Bawang          query='indomie kuah'            rank #1  top_score=0.598
  [PASS]  Mie Sedaap Goreng Original             query='mie sedap goreng'        rank #2  top_score=0.556
  [PASS]  Le Minerale Air Mineral 600ml          query='le mineral'              rank #1  top_score=0.708
  [PASS]  Aqua Air Mineral 600ml                 query='air aqua'                rank #1  top_score=0.708
  [PASS]  Teh Botol Sosro Original               query='teh botol'               rank #1  top_score=0.614
  [PASS]  Kopi Kapal Api Special Mix             query='kapal api mix'           rank #1  top_score=0.680
  [PASS]  Gula Pasir Rose Brand 1kg              query='gula rose brand'         rank #1  top_score=0.731
  [PASS]  Susu Kental Manis Frisian Flag Cokelat query='susu bendera cokelat'    rank #1  top_score=0.555
  [PASS]  Pocari Sweat 500ml                     query='pocari sweat'            rank #1  top_score=0.608
  [PASS]  Sabun Mandi Cair Lifebuoy              query='sabun lifebuoy merah'    rank #1  top_score=0.775

  Products: 11/11 passed

══════════════════════════════════════════════════════════════════════
  FAQ RETRIEVAL  (correct FAQ id must be top-1 result)
══════════════════════════════════════════════════════════════════════
  [PASS]  Cara pemesanan      query='cara melakukan pemesanan'          got_id=1   score=0.616
  [PASS]  Minimum pemesanan   query='minimum order berapa'              got_id=2   score=0.546
  [PASS]  Metode pembayaran   query='metode pembayaran yang tersedia'   got_id=3   score=0.665
  [PASS]  Lama pengiriman     query='berapa hari pengiriman'            got_id=4   score=0.756
  [PASS]  Biaya pengiriman    query='ongkos kirim gratis'               got_id=5   score=0.612
  [PASS]  Cek stok produk     query='cara cek stok barang'              got_id=6   score=0.692
  [PASS]  Negosiasi harga     query='harga bisa dinegosiasi'            got_id=7   score=0.727
  [PASS]  Produk rusak        query='barang rusak saat diterima'        got_id=8   score=0.661
  [PASS]  Produk non-katalog  query='pesan produk di luar katalog'      got_id=9   score=0.670
  [PASS]  Mitra reseller      query='daftar jadi reseller'              got_id=10  score=0.547
  [PASS]  Program loyalitas   query='program poin reward pelanggan'     got_id=11  score=0.809
  [PASS]  Batalkan pesanan    query='cara batalkan pesanan'             got_id=12  score=0.462
  [PASS]  Faktur/nota         query='minta faktur pembelian'            got_id=13  score=0.717
  [PASS]  Produk terlaris     query='produk paling laris'               got_id=14  score=0.573
  [PASS]  Kode promo          query='cara pakai kode promo'             got_id=15  score=0.786

  FAQs: 15/15 passed

══════════════════════════════════════════════════════════════════════
  INTENT CLASSIFICATION  (correct intent must be top-1 result)
══════════════════════════════════════════════════════════════════════
  [PASS]  Tambah jumlah item   query='tambah 3 lagi ke keranjang'                         score=0.421
  [PASS]  Tambah item ke cart  query='mau pesan 2 dus indomie goreng'                     score=0.195
  [PASS]  Pesan tanpa item     query='mau tambah ke keranjang tapi belum pilih produknya'  score=0.443
  [PASS]  Apply promo code     query='pakai kode DISC20'                                  score=0.719
  [PASS]  Pertanyaan umum      query='jam operasional toko berapa'                        score=0.666
  [PASS]  Lihat katalog        query='tampilkan katalog produk'                           score=0.791
  [PASS]  Tanya produk spesifik query='berapa harga susu bendera'                         score=0.195
  [PASS]  Batal tambah item    query='tidak jadi beli, batalkan'                          score=0.487
  [PASS]  Batal checkout       query='batalkan checkout'                                  score=0.661
  [PASS]  Checkout             query='checkout sekarang'                                  score=0.529
  [PASS]  Farewell             query='terima kasih sampai jumpa'                          score=0.472
  [PASS]  Cek produk favorit   query='cek produk favorit saya'                            score=0.665
  [PASS]  Greeting             query='halo selamat pagi'                                  score=0.479
  [PASS]  Tidak pakai promo    query='tidak pakai promo'                                  score=0.593
  [PASS]  Cek poin             query='berapa poin saya sekarang'                          score=0.529
  [PASS]  Status prioritas     query='saya pelanggan prioritas bukan'                     score=0.648
  [PASS]  Kurangi item         query='kurangi 1 dari keranjang'                           score=0.682
  [PASS]  Lihat keranjang      query='lihat isi keranjang saya'                           score=0.595

  Intents: 18/18 passed

══════════════════════════════════════════════════════════════════════
  SUMMARY
──────────────────────────────────────────────────────────────────────
  Products : 11/11
  FAQs     : 15/15
  Intents  : 18/18
──────────────────────────────────────────────────────────────────────
  TOTAL    : 44/44  (PASS)
══════════════════════════════════════════════════════════════════════
```

---

## Key Design Decisions

**Indonesian-specialist embedding model** — `LazarusNLP/all-indo-e5-small-v4` is a fine-tuned
E5 model trained specifically on Indonesian text (~33M params, ~120MB). Chosen over multilingual
alternatives (`paraphrase-multilingual-MiniLM-L12-v2`) because all data is in Indonesian.
E5 models require instruction prefixes: `"query: "` prepended to search queries at retrieval
time, `"passage: "` prepended to documents at index time. Both are applied automatically based
on `"e5" in EMBEDDING_MODEL_NAME`. Embedding texts in all data files are pure Indonesian to
maximise alignment — removing English boilerplate raised most intent classification scores by
0.1–0.24.

**LLM reranking for product disambiguation** — Embedding similarity alone cannot reliably
distinguish similar products (e.g. "indomie goreng" vs "indomie ayam bawang"). The retriever
fetches the top 5 candidates and the LLM selects the correct one from a numbered list. n=5
(not 3) is intentional: the E5 model places semantically similar FMCG products close together
in embedding space, so the correct product can sit at rank 3–5. This costs one extra embedding
call per product query.

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
| Embedding model | LazarusNLP/all-indo-e5-small-v4 (384 dimensions, ~33M params) |
| Model size | ~120MB (vs ~470MB for paraphrase-multilingual-MiniLM-L12-v2) |
| Language | Indonesian (specialist model, all data in Indonesian) |
| Total indexed items | 44 (11 products + 15 FAQs + 18 intents) |
| Retrieval accuracy | 44/44 (100%) on comprehensive test suite |
| Memory footprint | ~200MB with model loaded |
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

**Version**: 1.2.0 | **Status**: Production-ready
