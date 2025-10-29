#!/usr/bin/env python3
"""
Split google/genai/types.py into multiple organized files.

This script intelligently splits the massive 16K line types.py file into
smaller, logically organized modules for better import performance.
"""

import re
import os
from collections import defaultdict
from typing import List, Tuple, Set

# Read the original file
with open('google/genai/types/_types_original.py') as f:
    lines = f.readlines()

# Extract the header (copyright, imports, etc.)
header_end = 0
for i, line in enumerate(lines):
    if line.strip() and not line.startswith('#') and not line.startswith('from') and not line.startswith('import'):
        if not line.strip().startswith('if '):
            header_end = i
            break

header_lines = lines[:header_end]

# Find all class definitions with their line ranges
class_ranges = []
current_class = None
current_start = None
indent_level = 0

for i, line in enumerate(lines):
    # Check for class definition
    if re.match(r'^class \w+', line):
        # Save previous class if exists
        if current_class:
            class_ranges.append((current_class, current_start, i))

        # Start new class
        match = re.match(r'^class (\w+)', line)
        current_class = match.group(1)
        current_start = i
        indent_level = 0

# Don't forget the last class
if current_class:
    class_ranges.append((current_class, current_start, len(lines)))

print(f"Found {len(class_ranges)} classes")

# Categorize classes into files
file_assignments = defaultdict(list)

for class_name, start, end in class_ranges:
    # Determine which file this class belongs to
    if any(x in class_name for x in ['Enum', 'Outcome', 'Language', 'Type', 'Mode', 'Modality', 'Resolution', 'State', 'Task', 'Preference', 'Behavior', 'Level', 'Threshold', 'Method', 'Probability', 'Severity', 'Status', 'Reason', 'Traffic']):
        if 'Harm' not in class_name and 'Safety' not in class_name and 'Block' not in class_name:
            filename = 'enums.py'
        else:
            filename = 'safety.py'
    elif 'Content' in class_name or 'Part' in class_name or 'Blob' in class_name or 'Message' in class_name:
        filename = 'content.py'
    elif 'Generation' in class_name or 'Routing' in class_name or 'Config' in class_name and 'Safety' not in class_name:
        filename = 'generation.py'
    elif 'Safety' in class_name or 'Harm' in class_name or 'Block' in class_name:
        filename = 'safety.py'
    elif 'Function' in class_name and 'Tool' not in class_name:
        filename = 'functions.py'
    elif 'Tool' in class_name:
        filename = 'tools.py'
    elif 'Tuning' in class_name or 'Tuned' in class_name or 'Adapter' in class_name or 'Epoch' in class_name or 'Hyperparameters' in class_name:
        filename = 'tuning.py'
    elif 'File' in class_name:
        filename = 'files.py'
    elif 'Cache' in class_name or 'Cach' in class_name:
        filename = 'caching.py'
    elif class_name in ['Model', 'TunedModel', 'PreTunedModel', 'ModelSelectionConfig']:
        filename = 'models.py'
    elif 'Operation' in class_name:
        filename = 'operations.py'
    elif 'Request' in class_name or 'Response' in class_name:
        filename = 'requests.py'
    else:
        filename = 'common.py'

    file_assignments[filename].append((class_name, start, end))

# Print summary
print("\nSplit plan:")
for filename in sorted(file_assignments.keys()):
    print(f"  {filename}: {len(file_assignments[filename])} classes")

# Create the files
os.makedirs('google/genai/types', exist_ok=True)

for filename, classes in file_assignments.items():
    filepath = f'google/genai/types/{filename}'

    with open(filepath, 'w') as f:
        # Write header
        f.write(''.join(header_lines))
        f.write('\n\n')

        # Write classes
        for class_name, start, end in classes:
            class_lines = lines[start:end]
            f.write(''.join(class_lines))
            f.write('\n\n')

    print(f"Created {filepath} ({len(classes)} classes)")

print("\nDone!")
