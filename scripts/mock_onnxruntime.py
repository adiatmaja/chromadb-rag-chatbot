"""
Mock onnxruntime module for Docker compatibility.

This module provides a complete mock of onnxruntime to prevent ChromaDB
from crashing when onnxruntime is not available. ChromaDB will gracefully
fall back to using sentence-transformers with PyTorch backend.
"""

import sys
import types
from unittest.mock import MagicMock

# Create a proper module spec for the mock
class MockModuleSpec:
    def __init__(self, name):
        self.name = name
        self.loader = None
        self.origin = None
        self.submodule_search_locations = []
        self.cached = None
        self.parent = None

# Create a mock module type (not MagicMock)
class MockOnnxruntime(types.ModuleType):
    def __init__(self, name):
        super().__init__(name)
        self.__version__ = "1.16.3"
        self.__file__ = f"<mock {name}>"
        self.__package__ = name
        self.__spec__ = MockModuleSpec(name)
        self.InferenceSession = MagicMock()
        self.get_available_providers = lambda: ['CPUExecutionProvider']
        self.get_device = lambda: 'CPU'

    def __getattr__(self, name):
        # Return a MagicMock for any attribute access
        return MagicMock()

# Create mock modules
mock_ort = MockOnnxruntime('onnxruntime')
mock_ort_capi = MockOnnxruntime('onnxruntime.capi')
mock_ort_pybind = MockOnnxruntime('onnxruntime.capi._pybind_state')

# Set up parent-child relationships
mock_ort.capi = mock_ort_capi
mock_ort_capi._pybind_state = mock_ort_pybind

# Install the mock modules BEFORE any imports
sys.modules['onnxruntime'] = mock_ort
sys.modules['onnxruntime.capi'] = mock_ort_capi
sys.modules['onnxruntime.capi._pybind_state'] = mock_ort_pybind

print("✅ Installed complete onnxruntime mock for Docker compatibility")
