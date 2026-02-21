# Project Structure

This document describes the organization of the RAG Product Search System codebase.

## 📁 Directory Tree

```
nlp/
├── 📄 Core Files
│   ├── README.md                    # Main project documentation
│   ├── CLAUDE.md                    # Instructions for Claude Code
│   ├── CHANGELOG.md                 # Version history
│   ├── PROJECT_STRUCTURE.md         # This file
│   ├── requirements.txt             # Python dependencies
│   ├── .env                         # Environment configuration (not in git)
│   ├── .env.example                 # Environment template
│   ├── .gitignore                   # Git ignore rules
│   └── .dockerignore                # Docker ignore rules
│
├── 🐳 Docker Files
│   ├── Dockerfile                   # Docker image definition
│   └── docker-compose.yml           # Docker Compose configuration
│
├── 📚 docs/                         # All documentation
│   ├── README.md                    # Documentation index
│   ├── QUICK_START.md              # Quick start guide
│   ├── INTENT_SYSTEM.md            # Intent classification docs
│   ├── setup/                      # Setup guides
│   │   └── INDEXING_COMPLETE.md   # First-time setup summary
│   └── docker/                     # Docker-specific docs
│       ├── DOCKER_USAGE.md        # Docker usage guide
│       ├── FINAL_DOCKER_FIX.md   # Docker technical fixes
│       └── DOCKER_FIXES_SUMMARY.md # Fix summary
│
├── 🚀 deployment/                   # Deployment files
│   ├── DOCKER.md                    # Docker deployment guide
│   ├── DOCKER_QUICKSTART.md        # Docker quick start
│   ├── DOCKER_TEST.md              # Docker testing guide
│   ├── BUILD_OPTIMIZATION.md       # Build optimization notes
│   ├── deploy.sh                   # Linux deployment script
│   ├── deploy.bat                  # Windows deployment script
│   └── verify_docker.bat           # Docker verification
│
├── 🔧 scripts/                      # Utility scripts
│   ├── run_query.py                # Main interactive query interface
│   ├── mock_onnxruntime.py         # onnxruntime mock for Docker
│   ├── docker_run_query.py         # Docker wrapper for queries
│   ├── docker_entrypoint.sh        # Docker entrypoint script
│   ├── test_docker_mock.py         # Test onnxruntime mock
│   │
│   ├── indexing/                   # Data indexing scripts
│   │   ├── index_products.py      # Index product data
│   │   ├── index_faq.py           # Index FAQ data
│   │   ├── index_intent.py        # Index intent data
│   │   └── parse_intent_data.py   # Parse intent.txt to CSV
│   │
│   ├── testing/                    # Testing scripts
│   │   ├── test_intent_retrieval.py  # Test intent search
│   │   └── verify_collections.py     # Verify all collections
│   │
│   ├── demo/                       # Demonstration scripts
│   │   └── demo_full_workflow.py  # Full system demo
│   │
│   └── windows/                    # Windows helper scripts
│       ├── docker-setup-index.bat # Automated indexing setup
│       ├── docker-run-interactive.bat # Quick start interactive
│       └── docker-rebuild.bat     # Rebuild Docker container
│
├── 💾 src/                          # Source code
│   ├── config.py                    # Centralized configuration
│   │
│   ├── core/                       # Core business logic
│   │   ├── retriever.py           # Unified retrieval system
│   │   ├── orchestrator.py        # RAG orchestration
│   │   └── order_tracker.py       # Order tracking
│   │
│   └── utils/                      # Utility modules
│       ├── clickhouse_client.py   # ClickHouse integration
│       ├── stock_reader.py        # Stock data reader
│       └── helpers.py             # Helper functions
│
├── 📊 data/                         # Data files
│   ├── product_data.csv            # Product catalog
│   ├── stock_data.csv              # Stock/inventory data
│   ├── intent.txt                  # Intent definitions (raw)
│   └── intent_data.csv             # Parsed intent data
│
├── 🗄️ database/                     # Persistent storage
│   ├── chroma_db/                  # ChromaDB vector database
│   │   ├── fmcg_products/         # Product collection
│   │   ├── faq_collection/        # FAQ collection
│   │   └── intent_collection/     # Intent collection
│   └── orders.json                 # Tracked orders
│
├── 📝 logs/                         # Application logs
│   └── (generated at runtime)
│
├── 📦 examples/                     # Integration examples
│   ├── order_tracking_demo.py     # Order tracking example
│   └── api_integration_demo.py    # API integration example
│
└── 🧪 tests/                        # Test suite
    └── test_api.py                 # API tests

```

## 📄 Key Files Explained

### Root Level

**Configuration Files:**
- `.env` - Environment variables (API keys, database URLs, etc.)
- `.env.example` - Template for environment configuration
- `requirements.txt` - Python package dependencies

**Documentation:**
- `README.md` - Main project overview and getting started
- `CLAUDE.md` - Guidance for Claude Code when working with the project
- `CHANGELOG.md` - Version history and release notes
- `PROJECT_STRUCTURE.md` - This file

**Docker:**
- `Dockerfile` - Defines the Docker image
- `docker-compose.yml` - Docker Compose orchestration

### Source Code (`src/`)

**Configuration:**
- `config.py` - Centralized configuration loaded from .env

**Core Logic (`src/core/`):**
- `retriever.py` - UnifiedRetriever for searching across all collections
- `orchestrator.py` - UnifiedRAGOrchestrator for LLM integration
- `order_tracker.py` - OrderTracker for capturing customer orders

**Utilities (`src/utils/`):**
- `clickhouse_client.py` - ClickHouse database client for FAQs
- `stock_reader.py` - Direct CSV reader for stock data
- `helpers.py` - General utility functions

### Scripts (`scripts/`)

**Main Interface:**
- `run_query.py` - Interactive query system (main entry point)

**Docker-Specific:**
- `docker_run_query.py` - Wrapper that loads onnxruntime mock
- `docker_entrypoint.sh` - Container entry point
- `mock_onnxruntime.py` - Mock for onnxruntime compatibility

**Indexing (`scripts/indexing/`):**
- `index_products.py` - Index product catalog
- `index_faq.py` - Index FAQs from ClickHouse
- `parse_intent_data.py` - Parse raw intent definitions
- `index_intent.py` - Index parsed intents

**Windows Helpers (`scripts/windows/`):**
- `docker-setup-index.bat` - Automated first-time indexing
- `docker-run-interactive.bat` - Quick start for interactive mode
- `docker-rebuild.bat` - Rebuild and test Docker container

### Documentation (`docs/`)

**General:**
- `README.md` - Documentation index
- `QUICK_START.md` - Quick start guide
- `INTENT_SYSTEM.md` - Intent classification documentation

**Setup (`docs/setup/`):**
- `INDEXING_COMPLETE.md` - First-time setup completion summary

**Docker (`docs/docker/`):**
- `DOCKER_USAGE.md` - How to use Docker workflow
- `FINAL_DOCKER_FIX.md` - Technical details on Docker fixes
- `DOCKER_FIXES_SUMMARY.md` - Summary of resolved Docker issues

### Deployment (`deployment/`)

**Guides:**
- `DOCKER.md` - Complete Docker deployment guide
- `DOCKER_QUICKSTART.md` - Docker quick start
- `DOCKER_TEST.md` - Docker testing guide
- `BUILD_OPTIMIZATION.md` - Build optimization notes

**Scripts:**
- `deploy.sh` - Linux/Mac deployment script
- `deploy.bat` - Windows deployment script
- `verify_docker.bat` - Verify Docker installation

### Data (`data/`)

**Input Files:**
- `product_data.csv` - Product catalog with colloquial names
- `stock_data.csv` - Stock levels for inventory checking
- `intent.txt` - Raw intent definitions
- `intent_data.csv` - Parsed and structured intent data

### Database (`database/`)

**Vector Database:**
- `chroma_db/` - ChromaDB persistent storage
  - `fmcg_products/` - Product embeddings (11 items)
  - `faq_collection/` - FAQ embeddings (29 items)
  - `intent_collection/` - Intent embeddings (35 types)

**Order Tracking:**
- `orders.json` - Captured customer orders

## 🚦 Entry Points

### For Users

**Windows:**
```bash
# Quick start (interactive)
scripts\windows\docker-run-interactive.bat

# First-time setup (indexing)
scripts\windows\docker-setup-index.bat

# Rebuild container
scripts\windows\docker-rebuild.bat
```

**Linux/Mac:**
```bash
# Quick start
docker-compose up

# First-time setup
bash deployment/deploy.sh

# Interactive mode
python scripts/run_query.py
```

### For Developers

**Run Tests:**
```bash
pytest tests/
```

**Index Data:**
```bash
python scripts/indexing/index_products.py
python scripts/indexing/parse_intent_data.py
python scripts/indexing/index_intent.py
python scripts/indexing/index_faq.py
```

**Test Retrieval:**
```bash
python -m src.core.retriever
```

**Test Orchestrator:**
```bash
python -m src.core.orchestrator
```

## 📝 Configuration Files

### `.env` (Environment Variables)

Key configuration options:
- `LLM_BASE_URL` - LLM API endpoint
- `LLM_MODEL_NAME` - Model name
- `EMBEDDING_MODEL_NAME` - Embedding model
- `CLICKHOUSE_HOST` - ClickHouse host (for FAQs)
- `VECTOR_DB_PATH` - ChromaDB storage location

See `.env.example` for full list.

### `requirements.txt` (Dependencies)

Key packages:
- `chromadb==0.5.0` - Vector database
- `sentence-transformers==2.7.0` - Embeddings
- `torch==2.8.0` - PyTorch backend
- `openai==1.58.1` - LLM client
- `clickhouse-connect==0.8.11` - ClickHouse client

## 🔄 Data Flow

```
1. User Query
   ↓
2. scripts/run_query.py (or docker_run_query.py in Docker)
   ↓
3. src/core/orchestrator.py (UnifiedRAGOrchestrator)
   ↓
4. src/core/retriever.py (UnifiedRetriever)
   ↓
5. database/chroma_db/ (Vector Search)
   ↓
6. LLM Integration (Context + Query)
   ↓
7. Response to User
```

## 🎯 Quick Reference

| Task | Command | Location |
|------|---------|----------|
| Run system | `docker-compose up` | Root |
| Index data | `python scripts/indexing/index_*.py` | scripts/indexing/ |
| Test system | `pytest tests/` | tests/ |
| View docs | Open `docs/README.md` | docs/ |
| Deploy | `bash deployment/deploy.sh` | deployment/ |
| Windows setup | `scripts\windows\docker-setup-index.bat` | scripts/windows/ |

## 📖 Additional Notes

### Why This Structure?

1. **Separation of Concerns**: Code (src/), scripts (scripts/), docs (docs/)
2. **Docker-First**: All Docker-related files clearly organized
3. **Platform Scripts**: Windows scripts in scripts/windows/
4. **Clear Entry Points**: Main interfaces well documented
5. **Scalability**: Easy to add new components

### Recent Changes (v2.1)

- ✅ Moved all Docker docs to `docs/docker/`
- ✅ Moved setup docs to `docs/setup/`
- ✅ Moved Windows scripts to `scripts/windows/`
- ✅ Removed `version` from docker-compose.yml
- ✅ Added ChromaDB telemetry suppression
- ✅ Created documentation index
- ✅ Cleaned up root directory

---

**Last Updated**: November 18, 2025
**Version**: 2.1.0
