# FAQ Integration Guide - ClickHouse Edition

## 📋 Overview

This guide explains the FAQ system integration using **ClickHouse** as the data source. The system provides intelligent customer service by combining product search and FAQ answering in a unified interface.

---

## 🎯 What's New in Version 2.0

### ClickHouse Integration

- **Real-time Data**: FAQ data fetched directly from ClickHouse database
- **No CSV Files**: Eliminates manual CSV file management
- **Scalable**: Handle thousands of FAQs efficiently
- **Always Up-to-date**: Changes in ClickHouse reflect immediately after re-indexing

### Architecture Changes

1. **src/utils/clickhouse_client.py** - ClickHouse connection utilities
2. **index_faq.py** - Fetches from ClickHouse and indexes to ChromaDB
3. **src/core/retriever.py** - Unified search across products and FAQs
4. **src/core/orchestrator.py** - RAG pipeline with context-aware prompts

### Features

✅ **Dual Knowledge Base**: Products (CSV) + FAQs (ClickHouse)
✅ **Intelligent Routing**: Automatically determines content type
✅ **Real-time Updates**: Re-index to sync with ClickHouse
✅ **Context-Aware LLM**: Different prompts for products vs FAQs
✅ **Unified Interface**: Single query endpoint for all content

---

## 🚀 Quick Start

### Prerequisites

1. **Product system indexed**:
   ```bash
   # If product indexing exists, skip this
   # Otherwise run: python index_data.py
   ```

2. **ClickHouse accessible**:
   - Host, port, and database credentials
   - Table `your_database.faq` exists
   - Required columns: `id`, `question`, `answer`, `created_at`, `updated_at`, `language`

### Step 1: Configure ClickHouse Credentials

Edit `.env` file:

```env
# ClickHouse Configuration
CLICKHOUSE_HOST=clickhouse.sigmasolusi.com
CLICKHOUSE_PORT=80
CLICKHOUSE_DB_NAME=your_database
```

### Step 2: Install ClickHouse Client

```bash
pip install clickhouse-connect
```

### Step 3: Index FAQ Data

```bash
python index_faq.py
```

**Expected Output**:
```
══════════════════════════════════════════════════════════════════════
   FAQ Data Indexing (ClickHouse → ChromaDB)
══════════════════════════════════════════════════════════════════════

📥 Step 1: Fetching FAQ data from ClickHouse...
✅ Connected to ClickHouse at clickhouse.sigmasolusi.com:80
Database: your_database

📥 Fetching FAQ data from: your_database.faq
✅ Fetched 29 FAQ entries
Columns: ['id', 'question', 'answer', 'created_at', 'updated_at', 'language']

Sample FAQ entries:
┌───────┬────────────────────────────────────────────────────┐
│ ID    │ Question                                           │
├───────┼────────────────────────────────────────────────────┤
│ 1     │ bagaimana cara mendaftar?                          │
│ 2     │ bagaimana untuk menjadi mitra [company]?             │
│ 3     │ Daerah (yang disebutkan customer) bisa?            │
└───────┴────────────────────────────────────────────────────┘

💾 Step 2: Initializing ChromaDB...
✅ ChromaDB initialized

🤖 Step 3: Loading embedding model...
Model: all-MiniLM-L6-v2
✅ Model loaded

📦 Step 4: Setting up collection...
✅ Collection created

📝 Preparing FAQ data...
✅ Prepared 29 FAQ records

🔄 Step 5: Generating embeddings and indexing...
✅ Successfully indexed 29 FAQs!

══════════════════════════════════════════════════════════════════════
✨ FAQ Indexing Completed Successfully! ✨
══════════════════════════════════════════════════════════════════════

📊 Summary:
  • FAQs indexed: 29
  • Collection: faq_collection
  • Database: C:\Users\adi\PycharmProjects\nlp\database\chroma_db
```

### Step 4: Test Unified Search

```python
from src.core.retriever import UnifiedRetriever

retriever = UnifiedRetriever()

# Test FAQ search
result = retriever.search("bagaimana cara mendaftar?")
print(f"Type: {result.content_type}")
print(f"Question: {result.metadata['question']}")
print(f"Answer: {result.metadata['answer'][:100]}...")
```

### Step 5: Test Complete RAG System

```bash
python -m examples.order_tracking_demo
```

This demo includes both product and FAQ search capabilities.

---

## 🏗️ System Architecture

### Data Flow

```
┌─────────────────────┐
│  ClickHouse Server  │
│  your_database │
│      .faq table     │
└──────────┬──────────┘
           │ SQL Query
           ▼
┌─────────────────────┐
│  index_faq.py       │
│  - Fetch FAQ data   │
│  - Clean HTML       │
│  - Prepare text     │
└──────────┬──────────┘
           │ Embeddings
           ▼
┌─────────────────────┐
│    ChromaDB         │
│  faq_collection     │
│  - 29 FAQs          │
│  - Vector index     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  UnifiedRetriever   │
│  (src/core/)        │
│  - Search products  │
│  - Search FAQs      │
│  - Rank by score    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  RAG Orchestrator   │
│  - Context building │
│  - LLM processing   │
│  - Response gen     │
└─────────────────────┘
```

### Component Interaction

```
User Query: "bagaimana cara mendaftar?"
    ↓
[UnifiedRetriever]
    ↓
┌─────────────────┬─────────────────┐
│                 │                 │
│ Product Search  │  FAQ Search     │
│ (fmcg_products) │  (faq_coll.)    │
│ Score: 0.23     │  Score: 0.92    │
└─────────────────┴─────────────────┘
    ↓
[Best Match: FAQ, Score: 0.92]
    ↓
[RAG Orchestrator]
    ↓
[FAQ-specific System Prompt]
    ↓
[LLM Response]
```

---

## 📊 ClickHouse Table Structure

### Required Table Schema

```sql
CREATE TABLE your_database.faq (
    id Int32,
    question String,
    answer String,
    created_at DateTime,
    updated_at DateTime,
    language String
) ENGINE = MergeTree()
ORDER BY id;
```

### Sample Data

```sql
INSERT INTO your_database.faq VALUES
(1, 'bagaimana cara mendaftar?', '<p>Bila anda konsumen baru...</p>', now(), now(), 'indonesian'),
(2, 'bagaimana cara melakukan pemesanan?', '<p>Untuk melakukan pemesanan...</p>', now(), now(), 'indonesian');
```

### Data Requirements

- **id**: Unique integer identifier
- **question**: Natural language customer question
- **answer**: HTML or plain text answer
- **language**: Language code (e.g., "indonesian", "english")

**Note**: HTML tags in answers are preserved but can be cleaned during indexing if needed.

---

## 🔍 How Unified Search Works

### Search Process

1. **Query Embedding**: Convert user query to vector
2. **Parallel Search**: Query both collections simultaneously
3. **Relevance Ranking**: Compare scores across content types
4. **Best Match Selection**: Return highest scoring result
5. **Context Building**: Format data for LLM
6. **Response Generation**: Generate natural language response

### Relevance Scoring

Cosine similarity scores:
- **> 0.8**: Highly relevant match
- **0.6-0.8**: Moderately relevant
- **< 0.6**: Low relevance

### Content Type Detection

The system automatically detects content type:

```python
from src.core.retriever import ContentType

result = retriever.search("query")

if result.content_type == ContentType.PRODUCT:
    # Handle product result
    sku = result.metadata['sku']
    name = result.metadata['official_name']

elif result.content_type == ContentType.FAQ:
    # Handle FAQ result
    question = result.metadata['question']
    answer = result.metadata['answer']
```

---

## 🤖 LLM Integration

### Context-Aware System Prompts

The orchestrator uses different prompts based on content type:

#### For Products:

```python
SYSTEM_PROMPT_TEMPLATE = """
Anda adalah Asisten Penjualan E-commerce...

TIPE KONTEN: PRODUK
DATA KONTEKS:
- SKU: {sku}
- Nama: {official_name}
- Kemasan: {pack_size_desc}

TOOLS TERSEDIA:
- check_inventory(sku, requested_quantity)
"""
```

#### For FAQs:

```python
SYSTEM_PROMPT_TEMPLATE = """
Anda adalah Asisten Customer Service...

TIPE KONTEN: FAQ
DATA KONTEKS:
- Pertanyaan: {question}
- Jawaban: {answer}

Berikan jawaban yang informatif dan membantu.
"""
```

### Function Calling

- **Products**: Can trigger `check_inventory()` function
- **FAQs**: Direct information responses, no function calling

---

## 🔄 Updating FAQ Data

### When FAQ Data Changes in ClickHouse

1. **Update the database**: Make changes in ClickHouse
2. **Re-index**: Run `python index_faq.py`
3. **Automatic refresh**: New data immediately available

### Incremental Updates

For production environments, consider:

```python
# Example: Scheduled re-indexing
import schedule

def reindex_faqs():
    import subprocess
    subprocess.run(["python", "index_faq.py"])

# Re-index every hour
schedule.every().hour.do(reindex_faqs)
```

---

## 🛠️ Advanced Configuration

### Custom ClickHouse Query

Edit `src/utils/clickhouse_client.py` to customize the query:

```python
def fetch_faq_data(self, table_name: Optional[str] = None) -> pd.DataFrame:
    query = f"""
        SELECT
            id,
            question,
            answer,
            language
        FROM {table}
        WHERE language = 'indonesian'  -- Filter by language
        AND updated_at > now() - INTERVAL 30 DAY  -- Recent only
        ORDER BY id
    """
```

### Embedding Model Selection

For multilingual support, change model in `.env`:

```env
# Better for multilingual FAQs
EMBEDDING_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
```

### Multiple FAQ Collections

Create separate collections for different languages:

```python
# In index_faq.py
FAQ_COLLECTION_ID = "faq_collection_id"
FAQ_COLLECTION_EN = "faq_collection_en"
```

---

## 📈 Performance Optimization

### Caching Strategy

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_faq_response(question: str):
    result = retriever.search(question)
    return result
```

### Connection Pooling

```python
# Reuse ClickHouse connections
class ClickHousePool:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = clickhouse_connect.get_client(...)
        return cls._instance
```

### Batch Indexing

For large FAQ datasets:

```python
# Process in batches
batch_size = 100
for i in range(0, len(faqs), batch_size):
    batch = faqs[i:i+batch_size]
    collection.add(batch)
```

---

## 🧪 Testing

### Test FAQ Search

```python
from src.core.retriever import UnifiedRetriever, ContentType

retriever = UnifiedRetriever()

# Test cases
test_queries = [
    "bagaimana cara mendaftar?",
    "metode pembayaran apa saja?",
    "bagaimana cara tracking pesanan?",
]

for query in test_queries:
    result = retriever.search(query)
    assert result.content_type == ContentType.FAQ
    print(f"✅ {query}: {result.relevance_score:.2f}")
```

### Run Setup Script

```bash
python -m scripts.setup_faq
```

This validates:
- ClickHouse connectivity
- FAQ data quality
- Collection creation
- Search functionality

---

## ❓ Troubleshooting

### Issue: ClickHouse connection failed

**Error**: `Failed to connect to ClickHouse`

**Solutions**:
1. Verify credentials in `.env`
2. Test network connectivity: `ping clickhouse.sigmasolusi.com`
3. Check port is correct (usually 8123 for HTTP, 9000 for native)
4. Verify database name exists

### Issue: No FAQ data fetched

**Error**: `Fetched 0 FAQ entries`

**Solutions**:
1. Verify table exists: `SHOW TABLES FROM your_database`
2. Check table has data: `SELECT COUNT(*) FROM your_database.faq`
3. Verify column names match expected schema

### Issue: Collection not found

**Error**: `Collection 'faq_collection' not found`

**Solution**:
```bash
python index_faq.py
```

### Issue: Low relevance scores

**Cause**: Poor embedding quality or mismatched content

**Solutions**:
1. Improve FAQ question phrasing
2. Use multilingual embedding model
3. Increase `RETRIEVAL_TOP_K` to see more results
4. Check FAQ content quality

---

## 📚 Code Examples

### Complete Integration Example

```python
from src.core.retriever import UnifiedRetriever, ContentType
from src.core.orchestrator import UnifiedRAGOrchestrator

# Initialize
orchestrator = UnifiedRAGOrchestrator()

# Process queries
queries = [
    "Mau beli 3 dus Indomie",  # Product
    "Bagaimana cara mendaftar?",  # FAQ
]

for query in queries:
    result = orchestrator.retriever.search(query)

    if result.content_type == ContentType.PRODUCT:
        print(f"Product: {result.metadata['official_name']}")
        response = orchestrator.process_query(query)

    elif result.content_type == ContentType.FAQ:
        print(f"FAQ: {result.metadata['question']}")
        print(f"Answer: {result.metadata['answer']}")
```

---

## 🎯 Best Practices

1. **Regular Re-indexing**: Schedule periodic FAQ updates
2. **Monitor Performance**: Track search latency and accuracy
3. **Quality Control**: Review FAQ content regularly
4. **Error Handling**: Implement fallbacks for connection failures
5. **Logging**: Log all ClickHouse queries for debugging
6. **Testing**: Test FAQ changes in staging before production

---

## 📞 Support

For issues or questions:

1. Check ClickHouse connectivity
2. Verify table schema matches requirements
3. Review indexing logs for errors
4. Test with simple FAQ queries first
5. Consult main README.md for general troubleshooting

---

**FAQ system powered by ClickHouse + ChromaDB + RAG** 🚀
