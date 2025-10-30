#!/usr/bin/env python3
"""
Find all class inheritance relationships that need runtime imports
"""
import re
from collections import defaultdict
from pathlib import Path

modules = {}
for file in Path('google/genai/types').glob('*.py'):
    if file.name not in ['__init__.py']:
        module_name = file.stem
        with open(file) as f:
            modules[module_name] = f.read()

# Find all classes and their parents
class_to_module = {}
class_parents = {}

for module_name, content in modules.items():
    # Find class definitions with parents
    matches = re.findall(r'^class (\w+)\(([^)]+)\):', content, re.MULTILINE)
    for class_name, parents_str in matches:
        class_to_module[class_name] = module_name
        # Parse parent classes
        parents = [p.strip() for p in parents_str.split(',')]
        # Filter to just class names (not _common.BaseModel, etc.)
        parent_classes = [p for p in parents if '.' not in p and p and p[0].isupper() and p not in ['ABC', 'Enum', 'TypedDict', 'EnumMeta', 'BaseModel', 'Any']]
        if parent_classes:
            class_parents[class_name] = parent_classes

# Find cross-module inheritance
runtime_imports = defaultdict(set)
for class_name, parents in class_parents.items():
    module_name = class_to_module[class_name]
    for parent in parents:
        if parent in class_to_module:
            parent_module = class_to_module[parent]
            if parent_module != module_name:
                runtime_imports[module_name].add((parent_module, parent))

print("Runtime imports needed for inheritance:")
print("=" * 80)

for module in sorted(runtime_imports.keys()):
    imports = runtime_imports[module]
    by_module = defaultdict(list)
    for mod, cls in imports:
        by_module[mod].append(cls)

    print(f"\n{module}.py:")
    for mod in sorted(by_module.keys()):
        classes = sorted(by_module[mod])
        print(f"  from .{mod} import {', '.join(classes)}")

print("\n" + "=" * 80)
print(f"Total: {len(runtime_imports)} modules need runtime imports for inheritance")
