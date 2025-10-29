#!/usr/bin/env python3
"""
Split google/genai/types.py into organized modules with lazy loading.

This script carefully splits the massive types.py file while preserving
all imports, TYPE_CHECKING blocks, and class definitions.
"""

import re
import os
from collections import defaultdict
from typing import List, Tuple

print("Reading types.py...")
with open('google/genai/types.py') as f:
    content = f.read()
    lines = content.split('\n')

# Find where the first class starts
first_class_line = None
for i, line in enumerate(lines):
    if re.match(r'^class \w+', line):
        first_class_line = i
        break

if not first_class_line:
    raise ValueError("No classes found in types.py")

# Everything before the first class is the header
header = '\n'.join(lines[:first_class_line])

print(f"Header is {first_class_line} lines")
print(f"Total lines: {len(lines)}")

# Now extract all class definitions
# A class definition starts with "^class " and continues until the next "^class " or EOF
classes = []
current_class_name = None
current_class_start = None
current_class_lines = []

for i in range(first_class_line, len(lines)):
    line = lines[i]

    if re.match(r'^class \w+', line):
        # Save previous class
        if current_class_name:
            classes.append((current_class_name, '\n'.join(current_class_lines)))

        # Start new class
        match = re.match(r'^class (\w+)', line)
        current_class_name = match.group(1)
        current_class_lines = [line]
    else:
        if current_class_name:
            current_class_lines.append(line)

# Don't forget the last class
if current_class_name:
    classes.append((current_class_name, '\n'.join(current_class_lines)))

print(f"Extracted {len(classes)} classes")

# Categorize classes into files
file_assignments = defaultdict(list)

for class_name, class_content in classes:
    # Determine which file this class belongs to based on patterns
    if any(x in class_name for x in ['Enum', 'Outcome', 'Language', 'Type', 'Mode', 'Modality', 'Resolution', 'State', 'Task', 'Preference', 'Behavior', 'Level', 'Threshold', 'Method', 'Probability', 'Severity', 'Status', 'Reason', 'Traffic', 'Quality', 'Sensitivity', 'Handling', 'Coverage', 'Scale', 'Control', 'Environment']):
        if 'Harm' not in class_name and 'Safety' not in class_name and 'Block' not in class_name:
            filename = 'enums.py'
        else:
            filename = 'safety.py'
    elif 'Auth' in class_name:
        filename = 'auth.py'
    elif 'Rag' in class_name or 'Retrieval' in class_name or 'Search' in class_name:
        filename = 'retrieval.py'
    elif 'Grounding' in class_name or 'Ground' in class_name:
        filename = 'grounding.py'
    elif 'Batch' in class_name:
        filename = 'batch.py'
    elif 'Live' in class_name or 'Realtime' in class_name:
        filename = 'live.py'
    elif 'Embedding' in class_name or 'Embed' in class_name:
        filename = 'embeddings.py'
    elif 'Prompt' in class_name or 'Template' in class_name:
        filename = 'prompts.py'
    elif 'Chunk' in class_name or 'Corpus' in class_name or 'Document' in class_name:
        filename = 'documents.py'
    elif 'Schema' in class_name or 'JSONSchema' in class_name:
        filename = 'schema.py'
    elif 'Http' in class_name or 'ApiKey' in class_name or 'ApiAuth' in class_name or 'ApiSpec' in class_name:
        filename = 'http.py'
    elif 'Content' in class_name or 'Part' in class_name or 'Blob' in class_name or 'Message' in class_name:
        filename = 'content.py'
    elif 'Generation' in class_name:
        if 'Routing' in class_name:
            filename = 'routing.py'
        elif 'Thinking' in class_name:
            filename = 'thinking.py'
        else:
            filename = 'generation.py'
    elif 'Routing' in class_name or 'Route' in class_name:
        filename = 'routing.py'
    elif 'Thinking' in class_name or 'Think' in class_name:
        filename = 'thinking.py'
    elif 'FunctionCalling' in class_name:
        filename = 'generation.py'
    elif 'Safety' in class_name or 'Harm' in class_name or 'Block' in class_name:
        filename = 'safety.py'
    elif 'Function' in class_name and 'Tool' not in class_name:
        filename = 'functions.py'
    elif 'Tool' in class_name or 'Computer' in class_name or 'GoogleMaps' in class_name:
        filename = 'tools.py'
    elif 'Tuning' in class_name or 'Tuned' in class_name or 'Adapter' in class_name or 'Epoch' in class_name or 'Hyperparameters' in class_name:
        filename = 'tuning.py'
    elif 'File' in class_name:
        filename = 'files.py'
    elif 'Cache' in class_name or 'Cach' in class_name:
        filename = 'caching.py'
    elif 'Video' in class_name or 'Audio' in class_name or 'Music' in class_name:
        filename = 'media.py'
    elif 'Image' in class_name or 'Picture' in class_name:
        filename = 'images.py'
    elif 'Code' in class_name or 'Executable' in class_name:
        filename = 'code.py'
    elif class_name in ['Model', 'TunedModel', 'PreTunedModel', 'ModelSelectionConfig']:
        filename = 'models.py'
    elif 'Operation' in class_name:
        filename = 'operations.py'
    elif 'Request' in class_name or 'Response' in class_name:
        filename = 'responses.py'
    elif 'Metric' in class_name or 'Metadata' in class_name or 'Usage' in class_name:
        filename = 'metadata.py'
    elif 'Candidate' in class_name or 'Choice' in class_name or 'Citation' in class_name:
        filename = 'candidates.py'
    elif class_name.endswith('Config'):
        filename = 'configs.py'
    elif class_name.endswith('Options'):
        filename = 'options.py'
    elif 'Setting' in class_name:
        filename = 'settings.py'
    elif 'External' in class_name or 'Api' in class_name:
        filename = 'external.py'
    elif 'Parameters' in class_name or '_Get' in class_name or '_Create' in class_name or '_List' in class_name or '_Delete' in class_name or '_Update' in class_name:
        filename = 'parameters.py'
    elif 'Interval' in class_name or 'Time' in class_name or 'Date' in class_name:
        filename = 'temporal.py'
    elif 'Metric' in class_name or 'Score' in class_name or 'Eval' in class_name or 'Rouge' in class_name or 'Bleu' in class_name:
        filename = 'metrics.py'
    else:
        filename = 'base.py'

    file_assignments[filename].append((class_name, class_content))

# Print summary
print("\nSplit plan:")
for filename in sorted(file_assignments.keys(), key=lambda x: -len(file_assignments[x])):
    print(f"  {filename}: {len(file_assignments[filename])} classes")

# Create types directory
os.makedirs('google/genai/types', exist_ok=True)

# Fix imports in header for submodules
submodule_header = header.replace('from . import _common', 'from .. import _common')
submodule_header = submodule_header.replace('from ._operations_converters', 'from .._operations_converters')

# Create each file
for filename, class_list in file_assignments.items():
    filepath = f'google/genai/types/{filename}'

    with open(filepath, 'w') as f:
        # Write header
        f.write(submodule_header)
        f.write('\n\n')

        # Write all classes for this file
        for class_name, class_content in class_list:
            f.write(class_content)
            f.write('\n\n')

    size_kb = os.path.getsize(filepath) / 1024
    print(f"Created {filepath} ({len(class_list)} classes, {size_kb:.1f}KB)")

print(f"\nTotal files: {len(file_assignments)}")
print("Done!")
