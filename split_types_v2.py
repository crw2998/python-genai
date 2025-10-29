#!/usr/bin/env python3
"""
Split google/genai/types.py into multiple organized files (v2 - finer granularity).
"""

import re
import os
from collections import defaultdict

# Read the original file
with open('google/genai/types/_types_original.py') as f:
    lines = f.readlines()

# Extract the header
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

for i, line in enumerate(lines):
    if re.match(r'^class \w+', line):
        if current_class:
            class_ranges.append((current_class, current_start, i))
        match = re.match(r'^class (\w+)', line)
        current_class = match.group(1)
        current_start = i

if current_class:
    class_ranges.append((current_class, current_start, len(lines)))

print(f"Found {len(class_ranges)} classes")

# More granular categorization
file_assignments = defaultdict(list)

for class_name, start, end in class_ranges:
    # Enums first
    if any(x in class_name for x in ['Enum', 'Outcome', 'Language', 'Type', 'Mode', 'Modality', 'Resolution', 'State', 'Task', 'Preference', 'Behavior', 'Level', 'Threshold', 'Method', 'Probability', 'Severity', 'Status', 'Reason', 'Traffic', 'Quality', 'Sensitivity', 'Handling', 'Coverage', 'Scale', 'Control', 'Environment']):
        if 'Harm' not in class_name and 'Safety' not in class_name and 'Block' not in class_name:
            filename = 'enums.py'
        else:
            filename = 'safety.py'
    # Auth configs
    elif 'Auth' in class_name:
        filename = 'auth.py'
    # RAG and retrieval
    elif 'Rag' in class_name or 'Retrieval' in class_name or 'Search' in class_name:
        filename = 'retrieval.py'
    # Schema and validation
    elif 'Schema' in class_name or 'JSONSchema' in class_name:
        filename = 'schema.py'
    # HTTP and API configs
    elif 'Http' in class_name or 'ApiKey' in class_name or 'ApiAuth' in class_name or 'ApiSpec' in class_name:
        filename = 'http.py'
    # Content and messages
    elif 'Content' in class_name or 'Part' in class_name or 'Blob' in class_name or 'Message' in class_name:
        filename = 'content.py'
    # Generation configs
    elif 'Generation' in class_name or 'Routing' in class_name or 'FunctionCalling' in class_name:
        filename = 'generation.py'
    # Safety
    elif 'Safety' in class_name or 'Harm' in class_name or 'Block' in class_name:
        filename = 'safety.py'
    # Functions
    elif 'Function' in class_name and 'Tool' not in class_name:
        filename = 'functions.py'
    # Tools
    elif 'Tool' in class_name or 'Computer' in class_name or 'GoogleMaps' in class_name:
        filename = 'tools.py'
    # Tuning
    elif 'Tuning' in class_name or 'Tuned' in class_name or 'Adapter' in class_name or 'Epoch' in class_name or 'Hyperparameters' in class_name:
        filename = 'tuning.py'
    # Files
    elif 'File' in class_name:
        filename = 'files.py'
    # Caching
    elif 'Cache' in class_name or 'Cach' in class_name:
        filename = 'caching.py'
    # Video
    elif 'Video' in class_name or 'Audio' in class_name or 'Music' in class_name:
        filename = 'media.py'
    # Code execution
    elif 'Code' in class_name or 'Executable' in class_name:
        filename = 'code.py'
    # Models
    elif class_name in ['Model', 'TunedModel', 'PreTunedModel', 'ModelSelectionConfig']:
        filename = 'models.py'
    # Operations
    elif 'Operation' in class_name:
        filename = 'operations.py'
    # Requests/Responses
    elif 'Request' in class_name or 'Response' in class_name:
        filename = 'requests.py'
    # Metrics and metadata
    elif 'Metric' in class_name or 'Metadata' in class_name or 'Usage' in class_name:
        filename = 'metadata.py'
    # Candidates and choices
    elif 'Candidate' in class_name or 'Choice' in class_name or 'Citation' in class_name:
        filename = 'candidates.py'
    # Base types
    else:
        filename = 'base.py'

    file_assignments[filename].append((class_name, start, end))

# Print summary
print("\nSplit plan (v2):")
for filename in sorted(file_assignments.keys(), key=lambda x: -len(file_assignments[x])):
    print(f"  {filename}: {len(file_assignments[filename])} classes")

# Remove old split files
import glob
for old_file in glob.glob('google/genai/types/*.py'):
    if old_file != 'google/genai/types/_types_original.py' and old_file != 'google/genai/types/__init__.py':
        os.remove(old_file)
        print(f"Removed {old_file}")

# Create the files
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

    size_kb = os.path.getsize(filepath) / 1024
    print(f"Created {filepath} ({len(classes)} classes, {size_kb:.1f}KB)")

print("\nDone!")
