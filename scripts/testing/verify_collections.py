"""Verify all collections are working."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Docker compatibility - load before chromadb imports
sys.path.insert(0, str(Path(__file__).parent.parent))
import load_docker_compat

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

from src.core.retriever import UnifiedRetriever

print("\n=== Testing Unified Retriever ===\n")

# Initialize retriever
retriever = UnifiedRetriever()

print("\n=== Quick Test Queries ===\n")

# Test product search
print("1. Testing product search: 'indomie goreng'")
result = retriever.search("indomie goreng", search_products=True, search_faqs=False, search_intents=False)
if result:
    print(f"   ✓ Found: {result.metadata.get('official_name', 'N/A')}")
    print(f"   Confidence: {result.relevance_score:.2%}")
else:
    print("   ✗ No result")

print()

# Test intent search
print("2. Testing intent search: 'Checkout sekarang'")
result = retriever.search("Checkout sekarang", search_products=False, search_faqs=False, search_intents=True)
if result:
    print(f"   ✓ Found intent: {result.metadata.get('intent_name', 'N/A')}")
    print(f"   Confidence: {result.relevance_score:.2%}")
else:
    print("   ✗ No result")

print()

# Test combined search
print("3. Testing combined search: 'Saya ingin pesan indomie'")
result = retriever.search("Saya ingin pesan indomie", search_products=True, search_faqs=False, search_intents=True)
if result:
    print(f"   ✓ Best match type: {result.content_type.value.upper()}")
    print(f"   Confidence: {result.relevance_score:.2%}")
else:
    print("   ✗ No result")

print("\n=== All Tests Complete ===\n")
