"""Product data indexing script."""

import sys
import os

# Load onnxruntime mock for Docker compatibility (must be before chromadb)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
try:
    from mock_onnxruntime import *
except ImportError:
    pass

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

import chromadb
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer
from src.config import VECTOR_DB_PATH, EMBEDDING_MODEL_NAME, COLLECTION_NAME

PRODUCT_DATA_PATH = "data/product_data.csv"

print("\n=== Product Data Indexing ===\n")

# Load product data
print(f"Loading product data from {PRODUCT_DATA_PATH}...")
df = pd.read_csv(PRODUCT_DATA_PATH, encoding='utf-8')
print(f"Loaded {len(df)} products")

# Initialize ChromaDB
print("\nInitializing ChromaDB...")
Path(VECTOR_DB_PATH).mkdir(parents=True, exist_ok=True)
client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))
print("ChromaDB initialized")

# Load embedding model
print(f"\nLoading embedding model: {EMBEDDING_MODEL_NAME}...")
model = SentenceTransformer(EMBEDDING_MODEL_NAME)
print("Model loaded")

# Create/reset collection
print("\nSetting up collection...")
try:
    client.delete_collection(name=COLLECTION_NAME)
    print("Existing collection deleted")
except:
    pass

collection = client.create_collection(
    name=COLLECTION_NAME,
    metadata={"description": "FMCG product catalog embeddings", "hnsw:space": "cosine"}
)
print("Collection created")

# Prepare product data
print("\nPreparing product data...")
ids = []
documents = []
metadatas = []

for _, row in df.iterrows():
    sku = row['sku']
    embedding_text = row['embedding_text']

    ids.append(f"product_{sku}")
    documents.append(embedding_text)

    metadata = {
        'sku': sku,
        'official_name': str(row['official_name']),
        'colloquial_names': str(row['colloquial_names']),
        'pack_size_desc': str(row['pack_size_desc'])
    }

    metadatas.append(metadata)

print(f"Prepared {len(ids)} product records")

# Generate embeddings
print("\nGenerating embeddings...")
embeddings = model.encode(documents, show_progress_bar=False)
print(f"Generated embeddings: {embeddings.shape}")

# Add to ChromaDB
print("\nAdding to ChromaDB...")
collection.add(
    ids=ids,
    embeddings=embeddings.tolist(),
    documents=documents,
    metadatas=metadatas
)

# Verify
count = collection.count()
print(f"\nSuccessfully indexed {count} products!")
print(f"Collection: {COLLECTION_NAME}")
print(f"Database: {VECTOR_DB_PATH}")
print("\n=== Indexing Complete ===\n")
