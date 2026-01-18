import time
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from evaluation.metrics_exporter import PeriodicMetricsExporter
exp = PeriodicMetricsExporter(exporter='prometheus')
print('Before start, _prometheus_server=', exp._prometheus_server)
exp.start()
print('After start, _prometheus_server=', exp._prometheus_server)
# give it a moment
time.sleep(1)
try:
    import urllib.request
    print('scrape:', urllib.request.urlopen('http://127.0.0.1:9091/metrics', timeout=2).read().decode()[:200])
except Exception as e:
    print('scrape failed:', repr(e))
exp.stop()
print('Stopped; _prometheus_server=', exp._prometheus_server)
