"""
Docker Compatibility Helper.

This module loads the onnxruntime mock when running in Docker.
Import this at the very beginning of scripts that use ChromaDB.

Usage:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
    import load_docker_compat  # Must be before importing src modules
"""
import sys
import os

# Load onnxruntime mock for Docker compatibility
scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)

try:
    from mock_onnxruntime import *
    # Mock loaded successfully (we're in Docker or mock is available)
except ImportError:
    # Not in Docker or mock not needed, that's fine
    pass
