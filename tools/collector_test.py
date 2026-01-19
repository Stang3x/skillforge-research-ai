"""Collector mode smoke test: run a few queries and save exemplar outputs.

This is used by CI to verify exemplar collector-mode and generate artifacts.
"""
import json
from pathlib import Path
import os
import sys

# Ensure repository root is on sys.path so loaders work
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load the canonical researchassistant script by file path and re-export tools
import importlib.util
RA_PATH = ROOT / 'research-assistant' / 'researchassistant.py'
spec = importlib.util.spec_from_file_location('ra_module', str(RA_PATH))
ra = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ra)

search_web = ra.search_web
synthesize_findings = ra.synthesize_findings

OUT = Path('evaluation') / 'reports' / 'collector_examples.json'
OUT.parent.mkdir(parents=True, exist_ok=True)

QUERIES = [
    'Python programming language',
    'Machine learning basics',
    'Prompt engineering best practices'
]

results = []
for q in QUERIES:
    try:
        s = search_web(q)
    except Exception as e:
        s = f"ERROR: {e}"
    try:
        syn = synthesize_findings(q)
    except Exception as e:
        syn = f"ERROR: {e}"
    results.append({'query': q, 'search': s, 'synthesis': syn})

OUT.write_text(json.dumps({'examples': results}, indent=2), encoding='utf-8')
print(f"Wrote collector examples to: {OUT}")
