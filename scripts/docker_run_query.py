"""
Docker wrapper for run_query.py

This script loads the onnxruntime mock before importing ChromaDB
to prevent import errors in Docker containers where onnxruntime
has executable stack issues.
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the mock first (before any chromadb imports)
try:
    from mock_onnxruntime import *
except ImportError:
    print("Warning: Could not import onnxruntime mock")
    pass

# Now run the main query script
if __name__ == "__main__":
    # Import and run run_query
    with open(os.path.join(os.path.dirname(__file__), 'run_query.py'), 'r', encoding='utf-8') as f:
        code = f.read()
        exec(code)
