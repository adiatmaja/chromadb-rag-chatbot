# Changelog

All notable changes to this project are documented here.

## [2.0.1] - 2025-01-17

### Fixed

#### Windows Compatibility
- **onnxruntime DLL Error**: Fixed DLL loading issues on Windows
  - Downgraded from onnxruntime 1.23.2 to 1.16.3
  - Updated `requirements.txt` with pinned version
  - Added documentation in troubleshooting sections
  - Error: `ImportError: DLL load failed while importing onnxruntime_pybind11_state`

- **UTF-8 Encoding**: Fixed emoji/Unicode display errors on Windows console
  - Updated `scripts/setup_system.py` with UTF-8 configuration
  - Updated `scripts/setup_faq.py` with UTF-8 configuration
  - Added Rich Console legacy_windows=False setting
  - All setup scripts now work correctly on Windows

#### Script Fixes

- **setup_system.py**: Complete rewrite with fixes
  - Fixed import paths (src.config, src.core.retriever)
  - Fixed file path references to match current structure
  - Changed indexing to use subprocess for isolation
  - Added project root to sys.path
  - All checks now pass successfully

- **setup_faq.py**: Multiple improvements
  - Fixed import paths for ChromaDB and src modules
  - Added project root to sys.path
  - Changed FAQ indexing to subprocess-based execution
  - Fixed false negative in indexing status reporting
  - UTF-8 encoding fixes for Windows

#### Path Updates

- Updated all script file references:
  - `index_faq.py` → `scripts/indexing/index_faq.py`
  - `config.py` → `src/config.py`
  - `search_agent.py` → `src/core/retriever.py`

### Added

#### Product Catalog
- Added **Djarum 76** cigarette product to catalog
  - SKU: DJ011
  - Colloquial names: "Djarum Tujuh Enam; Rokok Djarum 76; Djarum 76 Kretek"
  - Pack size: 1 slop = 10 bungkus
  - Total products: **11** (was 10)

### Updated

#### Documentation
- **README.md**
  - Updated core dependencies with onnxruntime==1.16.3
  - Added Windows compatibility notes
  - Updated product count from 10 to 11
  - Expanded troubleshooting section with onnxruntime fix
  - Added setup script usage instructions
  - Updated system capabilities table

- **CLAUDE.md**
  - Added Version Compatibility section with onnxruntime details
  - Added Windows Compatibility section with code examples
  - Expanded troubleshooting section
  - Updated all script paths and commands
  - Documented UTF-8 encoding fix pattern

- **docs/QUICK_START.md**
  - Updated product count to 11
  - Updated expected output messages

- **docs/INTENT_SYSTEM.md**
  - Updated script paths to include full paths
  - Updated example counts (48 variations)

- **deployment/DOCKER_TEST.md**
  - Updated product count to 11 in expected outputs

#### Testing Status
All scripts in `scripts/` directory verified working:

**Indexing Scripts** (✅ 4/4 working):
- `parse_intent_data.py` - Parses 35 intents
- `index_intent.py` - Indexes 35 intents to ChromaDB
- `index_products.py` - Indexes 11 products
- `index_faq.py` - Indexes 29 FAQs from ClickHouse

**Testing Scripts** (✅ 2/2 working):
- `verify_collections.py` - Tests all collections
- `test_intent_retrieval.py` - Tests 20 intent queries

**Demo Scripts** (✅ 1/1 working):
- `demo_full_workflow.py` - Full RAG demo with LLM

**Main Scripts** (✅ 3/3 working):
- `setup_system.py` - System setup wizard
- `setup_faq.py` - FAQ integration wizard
- `run_query.py` - Interactive query interface

### Technical Details

#### Dependencies Updated
```
onnxruntime==1.16.3  # Critical: 1.20+ has Windows DLL issues
chromadb==0.5.0      # Critical: 1.3.4 causes segfaults
openai==1.58.1       # Fixed proxies compatibility
```

#### Current System State
- **Products**: 11 items indexed
- **FAQs**: 29 items from ClickHouse
- **Intents**: 35 types with 48 examples
- **Order Tracking**: 9 existing orders
- **LLM Integration**: ✅ Connected
- **All Scripts**: ✅ Working on Windows

### Breaking Changes
None - all changes are backward compatible.

### Migration Guide
If upgrading from previous version:

1. **Update onnxruntime**:
   ```bash
   pip uninstall -y onnxruntime
   pip install -r requirements.txt
   ```

2. **Re-index products** (to include Djarum 76):
   ```bash
   python scripts/indexing/index_products.py
   ```

3. **Test setup scripts**:
   ```bash
   python scripts/setup_system.py
   ```

### Known Issues
- None currently reported

### Contributors
- Fixed by: Claude Code Assistant
- Tested on: Windows 11, Python 3.10.0

---

## [2.0.0] - 2025-01-10

### Added
- Initial release with unified RAG system
- Product search, FAQ system, Intent classification
- Order tracking with CSV-based stock checking
- Docker deployment support

---

**Format**: This changelog follows [Keep a Changelog](https://keepachangelog.com/)
**Versioning**: Semantic Versioning [SemVer](https://semver.org/)
