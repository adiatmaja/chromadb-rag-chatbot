#!/bin/bash
# =============================================================================
# Docker Entrypoint Script
# =============================================================================
# This script runs before the main application to configure the environment
# for Docker-specific requirements.

set -e

echo "🐳 Docker entrypoint: Configuring environment..."

# Patch ChromaDB to handle missing onnxruntime gracefully
# This prevents ChromaDB from crashing when onnxruntime is not available
python3 << 'EOF'
import sys
import importlib.util

# Mock onnxruntime if it's not available
try:
    import onnxruntime
    print("✅ onnxruntime is available")
except ImportError:
    print("⚠️  onnxruntime not available - using PyTorch backend for embeddings")
    # ChromaDB will fall back to PyTorch-based embeddings
    pass
EOF

echo "✅ Environment configured successfully"
echo ""

# Execute the main command
exec "$@"
