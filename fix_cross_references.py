#!/usr/bin/env python3
"""
Automatically add TYPE_CHECKING imports for cross-referenced classes.

This script analyzes all type references in the split modules and adds
necessary imports to resolve NameErrors.
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import Set, Dict

# Read all modules
modules = {}
for file in Path('google/genai/types').glob('*.py'):
    if file.name not in ['__init__.py']:
        module_name = file.stem
        with open(file) as f:
            modules[module_name] = f.read()

# Find all class definitions in each module
class_to_module: Dict[str, str] = {}
for module_name, content in modules.items():
    classes = re.findall(r'^class (\w+)', content, re.MULTILINE)
    for cls in classes:
        class_to_module[cls] = module_name

print(f"Found {len(class_to_module)} classes across {len(modules)} modules")

# Analyze cross-references for each module
cross_refs: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))

for module_name, content in modules.items():
    # Find all class names referenced in this module
    # Look in:
    # 1. Type annotations: : Optional[ClassName]
    # 2. Type hints: list[ClassName], Union[ClassName, ...]
    # 3. Field types: ClassName = Field(...)
    # 4. Generic types: Sequence[ClassName]

    # Find all potential class references
    # This regex looks for capitalized words in type positions
    patterns = [
        r'Optional\[(\w+)\]',
        r'list\[(\w+)\]',
        r'Sequence\[(\w+)\]',
        r'Union\[([^\]]+)\]',
        r'dict\[\w+,\s*(\w+)\]',
        r':\s*(\w+)\s*=',  # : ClassName =
        r':\s*(\w+)\s*\n',  # : ClassName\n (end of line)
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # Handle Union which returns comma-separated classes
            if ',' in match:
                referenced_classes = [c.strip() for c in match.split(',')]
            else:
                referenced_classes = [match]

            for referenced_class in referenced_classes:
                # Clean up the class name
                referenced_class = referenced_class.strip()
                # Skip built-in types
                if referenced_class in ['int', 'str', 'bool', 'float', 'Any', 'None']:
                    continue
                # Skip if it starts with lowercase (not a class)
                if not referenced_class or not referenced_class[0].isupper():
                    continue

                if referenced_class in class_to_module:
                    ref_module = class_to_module[referenced_class]
                    # Skip self-references and http (already handled)
                    if ref_module != module_name and ref_module != 'http':
                        cross_refs[module_name][ref_module].add(referenced_class)

# Generate import statements for each module
print("\nGenerating imports...")
for module_name in sorted(cross_refs.keys()):
    imports_by_module = cross_refs[module_name]
    if not imports_by_module:
        continue

    filepath = f'google/genai/types/{module_name}.py'
    with open(filepath) as f:
        content = f.read()

    # Find where to insert imports (after the _operations_converters import block)
    lines = content.split('\n')
    insert_line = None

    for i, line in enumerate(lines):
        if line.startswith('from .._operations_converters import'):
            # Find the closing paren
            for j in range(i, len(lines)):
                if lines[j].strip() == ')':
                    insert_line = j + 1
                    break
            break

    if insert_line is None:
        print(f"Warning: Could not find insertion point in {module_name}.py")
        continue

    # Generate import statements
    import_lines = ['\n# Cross-module imports for type references']
    import_lines.append('if typing.TYPE_CHECKING:')
    for ref_module in sorted(imports_by_module.keys()):
        classes = sorted(imports_by_module[ref_module])
        # Split into chunks of 5 for readability
        for i in range(0, len(classes), 5):
            chunk = classes[i:i+5]
            import_lines.append(f'    from .{ref_module} import {", ".join(chunk)}')

    # Insert the imports
    new_lines = lines[:insert_line] + import_lines + lines[insert_line:]
    new_content = '\n'.join(new_lines)

    # Write back
    with open(filepath, 'w') as f:
        f.write(new_content)

    print(f"✓ Updated {module_name}.py ({len(imports_by_module)} modules imported)")

print("\nDone! All cross-references fixed.")
