"""Compatibility shim: expose `researchassistant.py` functions under the
`research_assistant` package name for backward compatibility.

This module loads the canonical script at `research-assistant/researchassistant.py`
and re-exports `search_web` and `synthesize_findings` so older imports like
`from research_assistant import search_web` continue to work.
"""
import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RA_PATH = PROJECT_ROOT / 'research-assistant' / 'researchassistant.py'

if not RA_PATH.exists():
    raise ImportError(f"researchassistant module not found at {RA_PATH}")

spec = importlib.util.spec_from_file_location('researchassistant_module', str(RA_PATH))
ra = importlib.util.module_from_spec(spec)
sys.modules['researchassistant_module'] = ra
spec.loader.exec_module(ra)

search_web = ra.search_web
synthesize_findings = ra.synthesize_findings

__all__ = ["search_web", "synthesize_findings"]
