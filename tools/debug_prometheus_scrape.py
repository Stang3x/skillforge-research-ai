import time
import urllib.request
import traceback
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from evaluation.metrics_exporter import PeriodicMetricsExporter

# Start exporter in prometheus mode
print('Starting PeriodicMetricsExporter in prometheus mode...')
exp = PeriodicMetricsExporter(token_tracker=None, cache=None, interval_seconds=1, exporter='prometheus', prometheus_port=9091)
exp.start()
print('Exporter.start() returned; waiting 2s for server to bind...')
time.sleep(2)

# attempt scrape
url = 'http://127.0.0.1:9091/metrics'
try:
    resp = urllib.request.urlopen(url, timeout=3)
    body = resp.read().decode('utf-8')
    print('SCRAPE SUCCESS:\n', body[:1000])
except Exception:
    print('SCRAPE FAILED; traceback:')
    traceback.print_exc()

# cleanup
try:
    exp.stop()
except Exception:
    pass
print('Done')
