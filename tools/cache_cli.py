"""
Cache CLI for SearchResultCache and LRUCacheWrapper

Usage:
  python tools/cache_cli.py stats
  python tools/cache_cli.py list
  python tools/cache_cli.py clear
  python tools/cache_cli.py inspect "some query"
"""
import sys
from pathlib import Path
import argparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure context-optimization is importable
CONTEXT = PROJECT_ROOT / 'context-optimization'
if str(CONTEXT) not in sys.path:
    sys.path.insert(0, str(CONTEXT))

from caching import SearchResultCache
from evaluation.cache_wrappers import LRUCacheWrapper


def main():
    parser = argparse.ArgumentParser(description="Cache CLI for SearchResultCache")
    sub = parser.add_subparsers(dest='cmd')

    sub.add_parser('stats', help='Show cache statistics')
    sub.add_parser('list', help='List cached entries')
    sub.add_parser('clear', help='Clear cache')
    sub.add_parser('reset', help='Reset cache hit/miss counters')
    sub.add_parser('reset-memory', help='Reset in-memory LRU hit/miss counters')
    export_p = sub.add_parser('export', help='Export cache metrics as JSON')
    export_p.add_argument('--file', '-f', help='Output file path (defaults to cache_metrics.json)', default='cache_metrics.json')

    inspect_p = sub.add_parser('inspect', help='Inspect cached result for a query')
    inspect_p.add_argument('query', help='Query string to inspect')

    args = parser.parse_args()

    cache_dir = str(Path.cwd() / 'cache')
    persistent = SearchResultCache(cache_dir=cache_dir, ttl_days=7)
    lru = LRUCacheWrapper(persistent_cache=persistent, capacity=256)

    if args.cmd == 'stats':
        s = lru.stats()
        print('Cache statistics:')
        for k, v in s.items():
            print(f'  {k}: {v}')
        return

    if args.cmd == 'list':
        items = persistent.list_cached_queries()
        if not items:
            print('No cached entries')
            return
        print('Cached entries (hash keys):')
        for it in items:
            print(' -', it)
        return

    if args.cmd == 'clear':
        persistent.clear()
        print('Cache cleared')
        return

    if args.cmd == 'reset':
        persistent.reset_metrics()
        print('Metrics reset')
        return

    if args.cmd == 'reset-memory':
        # Reset memory counters if available
        try:
            lru.memory_hits = 0
            lru.memory_misses = 0
            print('In-memory counters reset')
        except Exception:
            print('Could not reset in-memory counters')
        return

    if args.cmd == 'export':
        out = args.file
        try:
            import json
            s = lru.stats()
            Path(out).write_text(json.dumps(s, indent=2))
            print(f'Exported metrics to {out}')
        except Exception as e:
            print(f'Failed to export metrics: {e}')
        return

    if args.cmd == 'inspect':
        q = args.query
        val = lru.get(q)
        if val is None:
            print(f'No cache entry for: {q}')
            return
        print(f'Cached value for "{q}":')
        # Try pretty print
        try:
            import json
            print(json.dumps(val, indent=2, ensure_ascii=False))
        except Exception:
            print(val)
        return

    parser.print_help()


if __name__ == '__main__':
    main()
