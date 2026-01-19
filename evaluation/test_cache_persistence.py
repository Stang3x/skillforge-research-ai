"""
Persistence and TTL integration test for SearchResultCache.
Run: python evaluation/test_cache_persistence.py

Tests:
- Cache write and read
- Persistence across new SearchResultCache instance
- TTL expiration by setting file mtime in the past
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure context-optimization is importable
CONTEXT = PROJECT_ROOT / 'context-optimization'
if str(CONTEXT) not in sys.path:
    sys.path.insert(0, str(CONTEXT))

import caching as _caching


def main():
    cache_dir = str(Path.cwd() / 'test_cache_persistence')
    # Use a 1-day TTL for deterministic behavior
    pc = _caching.SearchResultCache(cache_dir=cache_dir, ttl_days=1)

    # Clean start
    pc.clear()

    query = 'persistence test'
    payload = [
        {"title": "PT1", "url": "https://example/pt1", "snippet": "payload"}
    ]

    # Store and verify immediate read
    pc.set(query, payload)
    read = pc.get(query)
    assert read is not None, 'Expected cache hit immediately after set'

    # New instance should read persisted file
    pc2 = _caching.SearchResultCache(cache_dir=cache_dir, ttl_days=1)
    read2 = pc2.get(query)
    assert read2 is not None, 'Expected persisted cache to be readable by new instance'

    # Locate cache file and simulate expiration by setting mtime to older than TTL
    key = pc._get_cache_key(query)
    cache_file = Path(cache_dir) / f"{key}.json"
    assert cache_file.exists(), 'Cache file must exist for TTL test'

    old_ts = (datetime.now() - timedelta(days=2)).timestamp()
    os.utime(cache_file, (old_ts, old_ts))

    # After forcing old mtime, get should return None and remove file
    expired = pc2.get(query)
    assert expired is None, 'Expected cache to be expired and return None'
    assert not cache_file.exists(), 'Expired cache file should be deleted by get()'

    print('Persistence & TTL integration test passed')


if __name__ == '__main__':
    main()
