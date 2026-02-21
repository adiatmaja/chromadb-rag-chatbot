"""
Test script to verify onnxruntime mock works correctly in Docker.
"""

import sys
import os

# Add scripts to path and import mock
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("Testing onnxruntime mock...")
print("=" * 60)

# Import the mock first
try:
    from mock_onnxruntime import *
    print("✅ Mock imported successfully")
except Exception as e:
    print(f"❌ Failed to import mock: {e}")
    sys.exit(1)

# Test that onnxruntime is in sys.modules
if 'onnxruntime' in sys.modules:
    print("✅ onnxruntime is in sys.modules")
    ort = sys.modules['onnxruntime']
    print(f"   - Version: {ort.__version__}")
    print(f"   - Spec: {ort.__spec__}")
    print(f"   - Spec.name: {ort.__spec__.name}")
else:
    print("❌ onnxruntime not in sys.modules")
    sys.exit(1)

# Test importing transformers (this was failing before)
try:
    print("\nTesting transformers import...")
    from transformers import AutoModel, AutoTokenizer
    print("✅ Transformers imported successfully")
except Exception as e:
    print(f"❌ Failed to import transformers: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test importing sentence_transformers
try:
    print("\nTesting sentence_transformers import...")
    from sentence_transformers import SentenceTransformer
    print("✅ SentenceTransformers imported successfully")
except Exception as e:
    print(f"❌ Failed to import sentence_transformers: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test importing chromadb
try:
    print("\nTesting chromadb import...")
    import chromadb
    print("✅ ChromaDB imported successfully")
except Exception as e:
    print(f"❌ Failed to import chromadb: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test creating a sentence transformer model
try:
    print("\nTesting SentenceTransformer model creation...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Model created successfully")

    # Test encoding
    print("\nTesting encoding...")
    embeddings = model.encode(['test query'])
    print(f"✅ Encoding successful, shape: {embeddings.shape}")
except Exception as e:
    print(f"❌ Failed to create/use model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nThe onnxruntime mock is working correctly.")
print("You can now run the main application.")
