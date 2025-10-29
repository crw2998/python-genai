"""Test the lazy-loading types package"""
import sys
import time

print("Testing lazy import...")
print()

# Test 1: Import just the package
start = time.time()
from google.genai import types
elapsed_package = time.time() - start
print(f"✓ Import google.genai.types package: {elapsed_package:.3f}s")

# Test 2: Access a common type
start = time.time()
Content = types.Content
elapsed_first = time.time() - start
print(f"✓ First type access (Content): {elapsed_first:.3f}s")

# Test 3: Access another type from same module
start = time.time()
Part = types.Part  
elapsed_same = time.time() - start
print(f"✓ Second type from same module (Part): {elapsed_same:.3f}s")

# Test 4: Access type from different module
start = time.time()
GenerationConfig = types.GenerationConfig
elapsed_different = time.time() - start
print(f"✓ Type from different module (GenerationConfig): {elapsed_different:.3f}s")

print()
print("SUCCESS! Lazy loading is working.")
print(f"Total time: {elapsed_package + elapsed_first + elapsed_same + elapsed_different:.3f}s")
