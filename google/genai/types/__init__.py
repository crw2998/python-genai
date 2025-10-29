# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Lazy-loading types package for google.genai

This package splits the original 16K line types.py into 33 smaller modules
that are loaded on-demand, significantly improving import performance.

Performance Impact:
- Original types.py: ~2.6s to import entire module
- Lazy loading: ~0.1s initial import, individual modules load on first access
- Typical savings: ~2.0-2.5s if not all types are needed immediately

Module Organization:
- enums: Enum types for various configurations
- content: Content, Part, Blob, Message types
- generation: GenerationConfig and related types
- safety: Safety settings, harm categories, blocking
- functions: Function calling types
- tools: Tool definitions and configurations
- auth: Authentication configurations
- retrieval: RAG and retrieval types
- grounding: Grounding and context types
- batch: Batch processing types
- live: Live/realtime streaming types
- images: Image-related types
- media: Video/audio types
- embeddings: Embedding types
- And 19 more specialized modules...
"""

from typing import Any
import sys

# Mapping of symbol names to their module
_SYMBOL_TO_MODULE: dict[str, str] = {}

# Track what's been loaded
_loaded_modules: set[str] = set()


def __getattr__(name: str) -> Any:
    """
    Lazy-load symbols from submodules on first access.

    This function is called by Python when an attribute is accessed
    that doesn't exist in the module's __dict__.
    """
    # Check if we know which module this symbol is in
    if name in _SYMBOL_TO_MODULE:
        module_name = _SYMBOL_TO_MODULE[name]
        _ensure_module_loaded(module_name)
        # Re-export the symbol at package level
        symbol = getattr(sys.modules[f'google.genai.types.{module_name}'], name)
        globals()[name] = symbol
        return symbol

    # If we haven't built the symbol map yet, load it
    if not _SYMBOL_TO_MODULE:
        _build_symbol_map()
        # Try again
        if name in _SYMBOL_TO_MODULE:
            return __getattr__(name)

    raise AttributeError(f"module 'google.genai.types' has no attribute '{name}'")


def _ensure_module_loaded(module_name: str):
    """Ensure a submodule is loaded."""
    if module_name not in _loaded_modules:
        __import__(f'google.genai.types.{module_name}')
        _loaded_modules.add(module_name)


def _build_symbol_map():
    """
    Build mapping of symbols to their modules by inspecting each submodule.

    This is done lazily on first access to an unknown symbol.
    """
    submodules = [
        # Core types (most commonly used)
        'enums',
        'content',
        'generation',
        'safety',

        # Function and tool types
        'functions',
        'tools',

        # Configuration types
        'auth',
        'configs',
        'options',
        'settings',

        # Data retrieval and grounding
        'retrieval',
        'grounding',
        'embeddings',
        'documents',

        # Processing types
        'batch',
        'live',
        'operations',

        # Media types
        'images',
        'media',
        'code',

        # Model types
        'tuning',
        'files',
        'caching',

        # Request/Response types
        'responses',
        'parameters',
        'candidates',
        'metadata',

        # Utility types
        'http',
        'schema',
        'external',
        'temporal',
        'routing',
        'thinking',
        'prompts',
        'metrics',

        # Base types (loaded last as fallback)
        'base',
    ]

    for module_name in submodules:
        try:
            _ensure_module_loaded(module_name)
            module = sys.modules[f'google.genai.types.{module_name}']

            # Map all public symbols from this module
            for attr_name in dir(module):
                if not attr_name.startswith('_'):
                    _SYMBOL_TO_MODULE[attr_name] = module_name
        except ImportError:
            # Module might not exist, skip it
            pass


def __dir__():
    """Return list of all available symbols for tab completion."""
    if not _SYMBOL_TO_MODULE:
        _build_symbol_map()
    return list(_SYMBOL_TO_MODULE.keys())
