"""Quick test to start PeriodicMetricsExporter in Prometheus mode and verify /metrics."""
import time
import urllib.request
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from evaluation.metrics_exporter import PeriodicMetricsExporter


def test_prometheus_scrape():
    """Pytest-compatible wrapper that runs the Prometheus scrape script once."""
    run_once()
    # Verify that the file artifact was written (CI expects this)
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metrics_export_ci.jsonl'))
    if not os.path.exists(file_path):
        raise AssertionError(f'Metrics file not written: {file_path}')
    # If strict mode enabled, ensure tokens observed > 0
    try:
        strict = bool(int(os.environ.get('METRICS_STRICT', '0')))
    except Exception:
        strict = False
    if strict:
        # read last line and inspect token totals
        try:
            with open(file_path, 'r', encoding='utf-8') as fh:
                lines = [l.strip() for l in fh.readlines() if l.strip()]
            if lines:
                last = json.loads(lines[-1])
                tt = last.get('token_tracker', {})
                if int(tt.get('total_tokens', 0) or 0) <= 0:
                    raise AssertionError('Strict mode: no tokens observed')
        except Exception:
            raise


def run_once():
    exp = PeriodicMetricsExporter(token_tracker=None, cache=None, interval_seconds=0.5, exporter='prometheus')
    exp.start()
    # Also start a file exporter to persist a metrics payload for CI artifact upload
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metrics_export_ci.jsonl'))
    try:
        os.remove(file_path)
    except Exception:
        pass
    file_exp = PeriodicMetricsExporter(token_tracker=None, cache=None, interval_seconds=0.5, exporter='file', filename=file_path)
    file_exp.start()
    # If METRICS_OTLP_URL is set in env, attempt to initialize the OTEL SDK to exercise exemplars/tracing
    otlp_url = os.environ.get('METRICS_OTLP_URL')
    if otlp_url:
        try:
            exp._start_opentelemetry_sdk(otlp_url=otlp_url, interval_seconds=0.5)
        except Exception:
            pass
    try:
        # give server a moment to bind and to let file exporter write
        time.sleep(1)
        # trigger a synchronous collection to ensure file payload exists
        try:
            file_exp.force_flush()
        except Exception:
            pass
        body = urllib.request.urlopen('http://127.0.0.1:9091/metrics', timeout=5).read().decode('utf-8')
        print('SCRAPE_OK')
        # assert token_total_tokens is present
        if 'token_total_tokens' not in body:
            print('EXPECTED_METRIC_MISSING')
            raise AssertionError('token_total_tokens not found in /metrics')
        # optional: ensure at least one token line exists
        lines = [l for l in body.splitlines() if l and not l.startswith('#')]
        if not any('token_total_tokens' in l for l in lines):
            print('NO_TOKEN_METRIC_SAMPLE')
            raise AssertionError('No token_total_tokens sample found')
        # print small sample
        print(lines[:20])
    except Exception as e:
        print('SCRAPE_FAIL', repr(e))
        raise
    finally:
        try:
            exp.stop()
        except Exception:
            pass
        try:
            file_exp.stop()
        except Exception:
            pass


if __name__ == '__main__':
    run_once()
