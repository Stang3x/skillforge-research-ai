#!/usr/bin/env python3
"""
Exemplar validation harness.

Modes:
 - direct: start a local HTTP `/metrics` server that exposes OpenMetrics text
   with an exemplar (trace_id) and then scrape it with the required Accept
   header to verify exemplar visibility.

 - collector: best-effort flow that attempts to create a trace/span (if
   OpenTelemetry is available) and then scrapes the configured collector URL
   (passed via --collector-url) with Accept: application/openmetrics-text to
   look for the trace id. This mode is diagnostic and best-effort.

Usage examples:
  python tools/exemplar_harness.py --mode direct
  python tools/exemplar_harness.py --mode collector --collector-url http://127.0.0.1:9464/metrics

"""
import argparse
import http.server
import json
import os
import random
import string
import socketserver
import threading
import time
import urllib.request


def gen_trace_id() -> str:
    # 32-hex char trace id (OTel-compatible)
    return ''.join(random.choice('0123456789abcdef') for _ in range(32))


class MetricsHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self._trace_id = kwargs.pop('trace_id')
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path != '/metrics':
            self.send_response(404)
            self.end_headers()
            return

        now_ms = int(time.time() * 1000)
        trace_id = self._trace_id
        content_lines = [
            '# HELP token_total_tokens Total tokens observed',
            '# TYPE token_total_tokens gauge',
            'token_total_tokens{tool="exemplar_harness"} 0.0',
            # OpenMetrics exemplar appended after a sample: 'value # {trace_id="..."} <timestamp_ms>'
            f'token_total_tokens{{tool="exemplar_harness"}} 0.0 # {{trace_id="{trace_id}"}} {now_ms}',
        ]
        body = '\n'.join(content_lines) + '\n'

        self.send_response(200)
        self.send_header('Content-Type', 'application/openmetrics-text; version=1.0.0; charset=utf-8')
        self.send_header('Content-Length', str(len(body.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))

    def log_message(self, format, *args):
        # silence default logging
        return


def run_direct_mode(host: str = '127.0.0.1', port: int = 8001, timeout: int = 5):
    trace_id = gen_trace_id()

    handler = lambda *args, **kwargs: MetricsHandler(*args, trace_id=trace_id, **kwargs)
    httpd = socketserver.TCPServer((host, port), handler)

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    try:
        url = f'http://{host}:{port}/metrics'
        req = urllib.request.Request(url, headers={'Accept': 'application/openmetrics-text'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode('utf-8')

        found = trace_id in text
        print(json.dumps({'mode': 'direct', 'trace_id': trace_id, 'scraped': found}))

        if not found:
            print('ERROR: exemplar trace_id not found in /metrics response')
            print('Response snippet:\n', text[:1000])
            return 2

        print('SUCCESS: exemplar found in direct-mode /metrics')
        return 0

    finally:
        httpd.shutdown()
        httpd.server_close()


def try_emit_trace(trace_id: str):
    # best-effort: attempt to create a span using OpenTelemetry if available
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        provider = TracerProvider()
        trace.set_tracer_provider(provider)
        tracer = trace.get_tracer(__name__)

        # Configure a no-op exporter if OTLP not configured; best-effort
        try:
            exporter = OTLPSpanExporter()
            provider.add_span_processor(SimpleSpanProcessor(exporter))
        except Exception:
            pass

        with tracer.start_as_current_span('exemplar-harness-span') as span:
            # set an attribute with our trace id so backends can correlate if needed
            span.set_attribute('harness.trace_id', trace_id)
            time.sleep(0.1)
        return True
    except Exception:
        return False


def run_collector_mode(collector_url: str, timeout: int = 5):
    trace_id = gen_trace_id()
    emitted = try_emit_trace(trace_id)
    if not emitted:
        print(json.dumps({'mode': 'collector', 'trace_id': trace_id, 'trace_emit': False, 'note': 'opentelemetry not available or failed; continuing'}))

    # wait briefly for exporter/collector to process
    time.sleep(0.5)

    req = urllib.request.Request(collector_url, headers={'Accept': 'application/openmetrics-text'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode('utf-8')
    except Exception as e:
        print(json.dumps({'mode': 'collector', 'trace_id': trace_id, 'scraped': False, 'error': str(e)}))
        return 2

    found = trace_id in text
    print(json.dumps({'mode': 'collector', 'trace_id': trace_id, 'scraped': found}))
    if not found:
        print('NOTE: exemplar not found on collector /metrics. This may be due to collector configuration, timing, or lack of exemplar support.')
        return 1

    print('SUCCESS: exemplar observed in collector /metrics')
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['direct', 'collector'], default='direct')
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8001)
    p.add_argument('--collector-url', help='Collector /metrics URL for collector mode')
    args = p.parse_args()

    if args.mode == 'direct':
        rc = run_direct_mode(host=args.host, port=args.port)
        raise SystemExit(rc)

    if args.mode == 'collector':
        if not args.collector_url:
            print('collector mode requires --collector-url')
            raise SystemExit(2)
        rc = run_collector_mode(args.collector_url)
        raise SystemExit(rc)


if __name__ == '__main__':
    main()
