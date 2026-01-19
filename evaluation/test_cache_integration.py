"""
Quick integration test for SearchResultCache + LRUCacheWrapper.
Run: python evaluation/test_cache_integration.py
"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load context-optimization caching module (not a package)
CONTEXT = PROJECT_ROOT / 'context-optimization'
if str(CONTEXT) not in sys.path:
    sys.path.insert(0, str(CONTEXT))
import caching as _caching
from evaluation.cache_wrappers import LRUCacheWrapper

cache_dir = str(Path.cwd() / 'test_cache')
pc = _caching.SearchResultCache(cache_dir=cache_dir, ttl_days=1)
lru = LRUCacheWrapper(persistent_cache=pc, capacity=8)

q = 'Integration test query'
val = 'Test result payload'

# Ensure clear
lru.clear()
assert lru.get(q) is None

lru.set(q, val)
read = lru.get(q)
print('Read from cache:', read)
assert read == val
print('LRU integration test passed')
