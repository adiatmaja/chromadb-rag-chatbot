# Intent Classification System

This document explains the intent mapping system integrated into the RAG-based search system.

## Overview

The intent classification system uses semantic search to identify user intentions from natural language queries in Indonesian (Bahasa Indonesia) and Javanese. It works similarly to the product and FAQ systems, using ChromaDB vector database for fast semantic matching.

## Architecture

```
┌─────────────────────────────────────────┐
│  User Query (Indonesian/Javanese)       │
│  "Saya ingin pesan 2 buah indomie"     │
└─────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────┐
│  Sentence Transformer                   │
│  (all-MiniLM-L6-v2)                    │
└─────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────┐
│  ChromaDB Vector Search                 │
│  - intent_collection                    │
└─────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────┐
│  Detected Intent                        │
│  intent_name: "add_item_to_cart"       │
│  confidence: 0.95                       │
└─────────────────────────────────────────┘
```

## Data Structure

The intent system maps:

- **Intent Name** (canonical query) → Official intent identifier (e.g., `add_item_to_cart`)
- **Description** → Clear explanation of what the intent means
- **Query Variations** (like colloquial names) → Example customer messages that map to this intent

This is analogous to the product system where:
- Product Name = Intent Name
- SKU = Intent Identifier
- Colloquial Names = Query Variations

## Setup and Usage

### 1. Parse Intent Data

First, convert the `intent.txt` file into structured CSV format:

```bash
python scripts/indexing/parse_intent_data.py
```

This creates `data/intent_data.csv` with 35 intents and 48 example variations.

### 2. Index Intents to ChromaDB

Index the intent data into the vector database:

```bash
python scripts/indexing/index_intent.py
```

This will:
- Load intent data from CSV
- Generate embeddings using sentence-transformers (all-MiniLM-L6-v2)
- Store in ChromaDB `intent_collection`
- Display indexing progress and summary

### 3. Test Intent Classification

Run the demo script to test intent detection:

```bash
python scripts/testing/test_intent_retrieval.py
```

This will test various Indonesian/Javanese queries and show detected intents with confidence scores.

### 4. Use in Your Application

```python
from src.core.retriever import UnifiedRetriever, ContentType

# Initialize retriever (loads all collections)
retriever = UnifiedRetriever()

# Classify user intent
result = retriever.search(
    query="Saya ingin pesan 2 buah indomie",
    search_products=False,
    search_faqs=False,
    search_intents=True  # Only search intents
)

if result and result.content_type == ContentType.INTENT:
    intent_name = result.metadata['intent_name']
    description = result.metadata['description']
    confidence = result.relevance_score

    print(f"Detected: {intent_name}")
    print(f"Description: {description}")
    print(f"Confidence: {confidence:.2%}")
```

## Available Intents

The system supports 35 intents including:

### Cart Operations
- `add_item_to_cart` - Customer wants to add specific items
- `add_item_to_cart_but_no_item_specified` - Wants to add items but didn't specify
- `remove_item_from_cart` - Remove items from cart
- `replace_item_from_cart` - Replace cart items
- `add_amount_of_item_in_cart` - Increase item quantity
- `change_amount_of_item_in_cart` - Change item quantity
- `reduce_amount_of_item_in_cart` - Decrease item quantity
- `cancel_adding_item_to_cart` - Cancel adding items

### Checkout & Payment
- `checkout` - Proceed to order submission
- `apply_promo_code` - Apply discount code
- `not_applying_promo_code` - Don't use promo
- `select_delivery_time` - Choose delivery time

### Account & Profile
- `question_about_customer_profile` - Check profile info
- `question_about_customer_profile_priority` - Check priority status
- `question_about_customer_profile_point` - Check loyalty points
- `register` - Customer wants to register

### Product Inquiries
- `asking_product_catalog` - Request product catalog
- `asking_promo_products` - Ask for promo items
- `asking_priority_products` - Ask for priority-member products
- `inquiry_of_product_availability` - Check if product is available
- `product_request` - Request unavailable product

### Favorite Products
- `check_favorite_products` - View favorite products list
- `start_favorite_product_stock_check` - Begin favorite stock check
- `continue_favorite_product_stock_check` - Continue stock check
- `favorite_product_stock_check_by_category` - Check by category
- `favorite_product_stock_check_direct` - Check directly

### Order Management
- `inquiry_of_order_history` - Ask about past orders
- `check_current_items_in_cart` - View cart contents

### Communication
- `greeting` - Customer greetings
- `farewell` - Saying goodbye
- `general_question` - General inquiries
- `complaint` - Customer complaints

### Other
- `message_not_supported` - Non-text message (image, audio, etc.)
- `others` - Different intent not covered above

## Integration with Existing System

The intent system seamlessly integrates with your existing product and FAQ search:

### Unified Search

```python
# Search across all knowledge bases
result = retriever.search(
    query="indomie kuning checkout",
    search_products=True,
    search_faqs=True,
    search_intents=True
)

# System automatically returns the best match
if result.content_type == ContentType.PRODUCT:
    # Handle product match
elif result.content_type == ContentType.FAQ:
    # Handle FAQ match
elif result.content_type == ContentType.INTENT:
    # Handle intent match
```

### Intent-Only Classification

```python
# For intent-focused applications (chatbots, command routing)
result = retriever.search(
    query=user_message,
    search_products=False,
    search_faqs=False,
    search_intents=True
)

intent = result.metadata['intent_name']
# Route to appropriate handler based on intent
```

## Configuration

The intent system uses the same configuration as other collections:

**.env settings:**
```bash
# Embedding model (shared across all collections)
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# Vector database path
VECTOR_DB_PATH=database/chroma_db

# Search settings
RETRIEVAL_TOP_K=3
```

**Collection name** (in `src/core/retriever.py`):
```python
INTENT_COLLECTION_NAME = "intent_collection"
```

## Data Files

- `intent.txt` - Original intent definitions and examples
- `data/intent_data.csv` - Structured intent data (auto-generated)
- `parse_intent_data.py` - Parser script
- `index_intent.py` - Indexing script
- `test_intent_retrieval.py` - Demo/test script

## Performance

- **Indexing**: ~1 second for 35 intents
- **Query time**: <100ms per query
- **Accuracy**: Depends on embedding model and query similarity
- **Scalability**: Can handle thousands of intents efficiently

## Adding New Intents

To add new intents:

1. **Edit `intent.txt`**:
   - Add intent name to the list
   - Add description with `** intent_name: description`
   - Add example queries in the examples section

2. **Re-parse and re-index**:
   ```bash
   python parse_intent_data.py
   python index_intent.py
   ```

3. **Test new intents**:
   ```bash
   python test_intent_retrieval.py
   ```

## Troubleshooting

### Intent collection not found
```bash
python index_intent.py
```

### Low confidence scores
- Add more query variations to `intent.txt`
- Ensure examples are in the target language (Indonesian/Javanese)
- Re-index after adding examples

### Wrong intent detected
- Add disambiguating examples
- Check for overlapping intent descriptions
- Adjust query variations to be more specific

## Future Enhancements

Potential improvements:
- Multi-lingual support beyond Indonesian/Javanese
- Intent confidence thresholds
- Intent fallback chains
- Context-aware intent detection
- Intent combination handling (multiple intents in one query)
