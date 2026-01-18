"""
Cache benchmark to exercise LRU and persistent cache and demonstrate memory hits/misses.

Usage: python tools/cache_benchmark.py
"""
import time
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
import sys
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure context-optimization import path
CONTEXT = PROJECT_ROOT / 'context-optimization'
if str(CONTEXT) not in sys.path:
    sys.path.insert(0, str(CONTEXT))

from caching import SearchResultCache
from evaluation.cache_wrappers import LRUCacheWrapper


def populate_cache(lru, n=50):
    for i in range(n):
        q = f"benchmark query {i}"
        payload = [{"title": f"Item {i}", "url": f"https://example/{i}", "snippet": "x"}]
        lru.set(q, payload)


def run_benchmark():
    cache_dir = str(Path.cwd() / 'cache')
    persistent = SearchResultCache(cache_dir=cache_dir, ttl_days=7)
    lru = LRUCacheWrapper(persistent_cache=persistent, capacity=128)

    print('Clearing cache and metrics...')
    persistent.clear()
    persistent._init_metrics()
    lru.memory_hits = 0
    lru.memory_misses = 0

    print('Populating cache...')
    populate_cache(lru, n=100)

    keys = [f"benchmark query {i}" for i in range(100)]

    # Warm-up: random access to fill LRU
    for _ in range(200):
        k = random.choice(keys)
        lru.get(k)

    # Measure many gets
    gets = 1000
    start = time.time()
    for _ in range(gets):
        k = random.choice(keys)
        lru.get(k)
    duration = time.time() - start

    stats = lru.stats()
    print('\nBenchmark results:')
    print(f'  Total gets performed: {gets}')
    print(f'  Duration (s): {duration:.4f}')
    print(f'  Avg get (ms): {duration * 1000.0 / gets:.3f}')
    print('  Memory hits:', getattr(lru, 'memory_hits', 0))
    print('  Memory misses:', getattr(lru, 'memory_misses', 0))
    print('  Persistent hits/writes/misses:', stats.get('hits'), stats.get('writes'), stats.get('misses'))
    print('\nCache stats:')
    for k, v in stats.items():
        print(' ', k, ':', v)


if __name__ == '__main__':
    run_benchmark()
