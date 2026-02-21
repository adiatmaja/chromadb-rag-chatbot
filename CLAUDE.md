# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# On Windows only — install after requirements.txt (excluded for Docker compatibility)
pip install onnxruntime==1.16.3

# Validate configuration
python src/config.py

# One-time data indexing (must be run in this order from project root)
python scripts/indexing/parse_intent_data.py   # intent.txt → intent_data.csv
python scripts/indexing/index_intent.py         # intent_data.csv → ChromaDB
python scripts/indexing/index_products.py       # product_data.csv → ChromaDB
python scripts/indexing/index_faq_csv.py        # data/faq_data.csv → ChromaDB (no-ClickHouse)
python scripts/indexing/index_faq.py            # ClickHouse → ChromaDB (production only)

# Verify all collections are indexed correctly
python scripts/indexing/verify_collections.py

# Interactive query interface (requires TTY — run in your own terminal, not via CI)
python scripts/run_query.py

# Docker
docker-compose up -d
docker-compose exec rag bash
docker-compose exec -it rag python scripts/run_query.py   # interactive session

# Docker indexing (after docker-compose up -d)
docker-compose exec rag python scripts/indexing/parse_intent_data.py
docker-compose exec rag python scripts/indexing/index_intent.py
docker-compose exec rag python scripts/indexing/index_products.py
docker-compose exec rag python scripts/indexing/index_faq_csv.py

# Rebuild Docker image (required after any changes to scripts/ or src/)
docker-compose build && docker-compose up -d

# API integration tests (requires API server running at localhost:8000)
python tests/test_api.py
python tests/test_api.py --endpoint health
python tests/test_api.py --endpoint check --sku IR001 --quantity 80
```

**Critical**: Always run scripts from the project root, not from inside `scripts/`. Import paths use `src.*` which requires the root as the working directory.

**Docker volume mounts**: Only `data/`, `database/`, and `logs/` are volume-mounted. Changes to `src/` or `scripts/` require `docker-compose build` to take effect, or use `docker cp <file> <container>:/app/<file>` for quick iteration.

## Architecture

The system is a unified RAG pipeline with three ChromaDB collections searched in parallel on every query:

```
User Query
    │
    ▼
UnifiedRetriever (src/core/retriever.py)
    │  sentence-transformers embeds query → search 3 collections
    ├──▶ fmcg_products collection   (product catalog, SKUs)
    ├──▶ faq_collection             (FAQ data)
    └──▶ intent_collection          (35+ e-commerce intents)
         │
         ▼  best match by relevance_score (1 - cosine_distance)
UnifiedRAGOrchestrator (src/core/orchestrator.py)
    │  builds LLM context, calls OpenAI-compatible API (LM Studio / any provider)
    │
    ├── if PRODUCT → get_product_candidates(query, n=5)
    │       │  fetches top 5 products, formats numbered list for LLM reranking
    │       │  LLM selects the most relevant product from candidates
    │       │
    │       └── if explicit quantity → function call: check_inventory(sku, qty)
    │               │
    │               ▼
    │           StockReader (src/utils/stock_reader.py)  ← reads data/stock_data.csv
    │               │
    │               ▼
    │           OrderTracker (src/core/order_tracker.py) ← saves to database/orders.json
    │
    └── final LLM response (Indonesian language)
```

**Key design choices:**
- **ChromaDB collection names**: `fmcg_products` (from `COLLECTION_NAME` env var), `faq_collection` and `intent_collection` are hardcoded constants in `retriever.py` — not env vars.
- **Product reranking**: For PRODUCT matches, `get_product_candidates()` runs a second embedding lookup to fetch the top 5 products, which are sent to the LLM as a numbered list. The LLM selects the correct product — this handles cases where embedding similarity alone picks the wrong variant (e.g., "indomie goreng" vs "indomie ayam bawang"). n=5 (not 3) is intentional: the `paraphrase-multilingual-MiniLM-L12-v2` model places semantically similar Indonesian products close together, so the correct product may sit at rank 3–5. This means two embedding calls per product query.
- **Stock data**: Read directly from `data/stock_data.csv` via `StockReader`. Schema requires: `sku`, `product_name`, `warehouse_id`, `warehouse_name`, `location`, `quantity`, `reserved_quantity`, `reorder_level`. Supports multiple rows per SKU (multi-warehouse). The `src/api/inventory_api.py` is a legacy FastAPI module not used in the current flow.
- **Cosine distance**: All ChromaDB collections must be created with `metadata={"hnsw:space": "cosine"}`. Default L2 distance makes `relevance_score = 1 - distance` always return 0 for typical embedding distances.
- **Order tracking**: `OrderTracker` persists orders to `database/orders.json` as a flat list of `OrderData` dataclasses.
- **`run_query.py` requires TTY**: Uses `input()` — cannot be run via non-interactive shells (e.g., `docker-compose exec` without `-it`).

## Configuration

All config lives in `.env` (copy from `.env.example`). Config is loaded centrally in `src/config.py` and imported by all modules. Key variables:

```env
LLM_BASE_URL=http://localhost:1234/v1              # Any OpenAI-compatible endpoint
LLM_MODEL_NAME=qwen2.5-7b-instruct               # Must match name shown in LM Studio
EMBEDDING_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2  # Best for Indonesian/Javanese
COLLECTION_NAME=fmcg_products
VECTOR_DB_PATH=database/chroma_db
RETRIEVAL_TOP_K=1
```

Changing `EMBEDDING_MODEL_NAME` requires full re-indexing of all three collections.

## Dependency Constraints

These versions are pinned and must not be changed without compatibility testing:

| Package | Pinned Version | Reason |
|---------|---------------|--------|
| `chromadb` | 0.5.0 | 1.3.4 causes segfaults on Windows with torch 2.8.0 |
| `sentence-transformers` | 2.7.0 | 5.x incompatible with torch 2.8.0 |
| `torch` | 2.8.0 | Required by sentence-transformers |
| `rich` | 13.0.0 | 14.x conflicts with streamlit |
| `onnxruntime` | 1.16.3 | Excluded from requirements.txt (Docker); install manually on Windows |

## Data Files

- `data/product_data.csv` — Product catalog (SKUs, official names, colloquial names, pack sizes, pre-computed `embedding_text`)
- `data/stock_data.csv` — Inventory by warehouse (columns: `sku`, `product_name`, `warehouse_id`, `warehouse_name`, `location`, `quantity`, `reserved_quantity`, `reorder_level`)
- `data/faq_data.csv` — FAQ entries for no-ClickHouse mode
- `data/intent.txt` — Raw intent definitions → parsed by `parse_intent_data.py` → `data/intent_data.csv`
- `database/chroma_db/` — ChromaDB persistent storage (git-ignored)
- `database/orders.json` — Persistent order tracking (git-ignored)
