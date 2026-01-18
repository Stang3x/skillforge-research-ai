"""Run a short non-interactive local demo of the PeriodicMetricsExporter.

This script creates a TokenTracker and a small cache, records sample events,
starts the exporter (1s interval), waits a few seconds, then stops the exporter
and prints the output file path.
"""
import time
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from evaluation.token_tracker import TokenTracker
# context-optimization uses a hyphen in the folder name; import its modules by adding that folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'context-optimization')))
from caching import SearchResultCache
from evaluation.cache_wrappers import LRUCacheWrapper
from evaluation.metrics_exporter import PeriodicMetricsExporter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prometheus', '-p', action='store_true', help='Also start Prometheus /metrics server')
    parser.add_argument('--duration', '-d', type=int, default=6, help='Seconds to run the exporter (when prometheus enabled, keep server up to allow scrapes)')
    args = parser.parse_args()
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    out_file = os.path.join(project_root, 'metrics_export_local_demo.jsonl')
    # ensure clean
    try:
        os.remove(out_file)
    except Exception:
        pass

    tt = TokenTracker(storage=os.path.join(project_root, 'evaluation', 'token_tracker_demo.json'))
    cache = SearchResultCache(cache_dir=os.path.join(project_root, 'cache_demo'), ttl_days=1)
    lru = LRUCacheWrapper(persistent_cache=cache, capacity=64)

    # record some sample events
    tt.record_request(prompt='demo:hello', completion='hello world', meta={'demo': True})
    lru.set('demo query 1', 'result 1')
    lru.get('demo query 1')
    tt.record_request(prompt='demo:search', completion='found something', meta={'demo': True})

    # start file exporter
    exporter = PeriodicMetricsExporter(token_tracker=tt, cache=lru, interval_seconds=1, exporter='file', filename=out_file)
    exporter.start()
    exporters = [exporter]
    print(f"File exporter started, writing to: {out_file}")

    # optionally start Prometheus server in parallel so /metrics is available
    prom_exporter = None
    if args.prometheus:
        prom_exporter = PeriodicMetricsExporter(token_tracker=tt, cache=lru, interval_seconds=1, exporter='prometheus')
        prom_exporter.start()
        exporters.append(prom_exporter)
        print("Prometheus exporter started at http://127.0.0.1:9091/metrics")

    # let it run for a few cycles (longer if prometheus to allow scraping)
    time.sleep(args.duration)

    for e in exporters:
        try:
            e.force_flush()
        except Exception:
            pass
        try:
            e.stop()
        except Exception:
            pass

    # report results
    if os.path.exists(out_file):
        print(f"Demo completed — metrics written to: {out_file}")
        with open(out_file, 'r', encoding='utf-8') as fh:
            lines = [l.strip() for l in fh.readlines() if l.strip()]
        print(f"Wrote {len(lines)} lines; sample:\n", '\n'.join(lines[:2]))
    else:
        print("Demo failed — metrics file not created")


if __name__ == '__main__':
    main()
