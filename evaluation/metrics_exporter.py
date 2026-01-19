import threading
import time
import json
import datetime
import traceback
import urllib.request
import urllib.error
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
try:
    from prometheus_client import start_http_server, Gauge, Counter, Histogram, CollectorRegistry
except Exception:
    start_http_server = None
    Gauge = None
    Counter = None
    Histogram = None
    CollectorRegistry = None


class PeriodicMetricsExporter:
    """Periodic exporter with multiple targets:

    - console: print JSON payloads
    - file: append newline-delimited JSON to a file
    - otlp: POST JSON to a configurable OTLP-like endpoint (best-effort)
    - prometheus: expose a /metrics HTTP endpoint with simple Prometheus text format

    This is intentionally lightweight and dependency-free so it works in CI
    and local test environments without extra packages.
    """

    def __init__(self, token_tracker=None, cache=None, interval_seconds=60, exporter="console", filename="metrics_export.json", otlp_url=None, prometheus_port=9091):
        self.token_tracker = token_tracker
        self.cache = cache
        self.interval = float(interval_seconds)
        self.exporter = exporter
        self.filename = filename
        self.otlp_url = otlp_url
        self.prometheus_port = int(prometheus_port)

        self._stop_event = threading.Event()
        self._thread = None
        self._prometheus_server = None
        self._latest_payload = None
        self._prom_registry = None
        self._prom_metrics = {}

    def _collect(self):
        payload = {"timestamp": datetime.datetime.utcnow().isoformat() + "Z"}

        if self.token_tracker is not None:
            try:
                payload["token_tracker"] = self.token_tracker.summary()
                # derive per-tool counts and averages from records if available
                try:
                    records = getattr(self.token_tracker, 'records', []) or []
                    per_tool = {}
                    for r in records:
                        meta = r.get('meta', {}) if isinstance(r, dict) else {}
                        tool = meta.get('tool', 'unknown')
                        entry = per_tool.setdefault(tool, {'count': 0, 'tokens_total': 0})
                        entry['count'] += 1
                        entry['tokens_total'] += int(r.get('tokens', 0) or 0)
                    # compute averages
                    for k, v in per_tool.items():
                        v['avg_tokens'] = (v['tokens_total'] / v['count']) if v['count'] else 0
                    payload['token_tracker']['per_tool'] = per_tool
                except Exception:
                    payload['token_tracker']['per_tool_error'] = traceback.format_exc()
            except Exception:
                payload["token_tracker_error"] = traceback.format_exc()

        if self.cache is not None:
            try:
                payload["cache"] = self.cache.stats()
                # derive hit ratios if stats available
                try:
                    cs = payload['cache']
                    gets = cs.get('gets', 0) or 0
                    hits = cs.get('hits', 0) or 0
                    mem_hits = cs.get('memory_hits', 0) or 0
                    cs['hit_ratio'] = (hits / gets) if gets else None
                    cs['memory_hit_ratio'] = (mem_hits / gets) if gets else None
                except Exception:
                    payload['cache']['derive_error'] = traceback.format_exc()
            except Exception:
                payload["cache_error"] = traceback.format_exc()

        self._latest_payload = payload
        return payload

    def _get_latest_trace_id(self):
        # Best-effort: if OpenTelemetry tracing is available, attempt to get current span trace id
        try:
            from opentelemetry import trace as ot_trace
            span = ot_trace.get_current_span()
            if span is None:
                return None
            ctx = span.get_span_context()
            if not ctx or not hasattr(ctx, 'trace_id'):
                return None
            return format(ctx.trace_id, '032x')
        except Exception:
            return None

    def _export_console(self, payload):
        print(json.dumps(payload, indent=2))

    def _export_file(self, payload):
        try:
            with open(self.filename, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload) + "\n")
        except Exception:
            print("Failed to write metrics to file:", self.filename)
            print(traceback.format_exc())

    def _export_otlp(self, payload):
        # Best-effort HTTP POST JSON to configured OTLP URL
        if not self.otlp_url:
            return
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.otlp_url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=max(5, self.interval)) as resp:
                # ignore response body; just ensure success
                resp.read()
        except Exception:
            print(f"[OTLP] Failed to POST metrics to {self.otlp_url}")
            print(traceback.format_exc())

    def _start_prometheus(self):
        if self._prometheus_server:
            return
        # Prefer using prometheus_client if available
        if start_http_server and Gauge is not None:
            try:
                self._prom_registry = CollectorRegistry()
                # create gauges/counters/histograms we'll update on each collect
                # include optional trace_id label for exemplars/trace correlation
                self._prom_metrics['token_total_tokens'] = Gauge('token_total_tokens', 'Total tokens observed', ['tool', 'trace_id'], registry=self._prom_registry)
                self._prom_metrics['token_requests'] = Gauge('token_requests_total', 'Requests per tool', ['tool', 'trace_id'], registry=self._prom_registry)
                self._prom_metrics['token_avg'] = Gauge('token_avg_tokens', 'Average tokens per request', ['tool', 'trace_id'], registry=self._prom_registry)
                self._prom_metrics['cache_entries'] = Gauge('cache_entries', 'Cache entries')
                self._prom_metrics['cache_writes'] = Gauge('cache_writes_total', 'Cache writes total')
                self._prom_metrics['cache_hits'] = Gauge('cache_hits_total', 'Cache hits total')
                # start HTTP server
                start_http_server(self.prometheus_port, registry=self._prom_registry)
                self._prometheus_server = True
                return
            except Exception:
                print("Failed to start prometheus_client server:\n", traceback.format_exc())

        # Fallback: use simple HTTP handler if prometheus_client not available
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self_inner):
                if self_inner.path != "/metrics":
                    self_inner.send_response(404)
                    self_inner.end_headers()
                    return
                payload = self._latest_payload or {}
                lines = []
                tt = payload.get("token_tracker") or {}
                trace_id = self._get_latest_trace_id() or ''
                # include trace_id as label in the fallback text format
                if trace_id:
                    lines.append(f'token_total_tokens{{trace_id="{trace_id}"}} {tt.get("total_tokens", 0)}')
                    lines.append(f'token_total_cost{{trace_id="{trace_id}"}} {tt.get("total_cost", 0.0)}')
                    lines.append(f'token_records{{trace_id="{trace_id}"}} {tt.get("records", 0)}')
                else:
                    lines.append(f"token_total_tokens {tt.get('total_tokens', 0)}")
                    lines.append(f"token_total_cost {tt.get('total_cost', 0.0)}")
                    lines.append(f"token_records {tt.get('records', 0)}")
                c = payload.get("cache") or {}
                lines.append(f"cache_entries {c.get('entries', 0)}")
                lines.append(f"cache_writes {c.get('writes', 0)}")
                lines.append(f"cache_hits {c.get('hits', 0)}")

                body = "\n".join(lines) + "\n"
                self_inner.send_response(200)
                self_inner.send_header("Content-Type", "text/plain; version=0.0.4")
                self_inner.send_header("Content-Length", str(len(body.encode("utf-8"))))
                self_inner.end_headers()
                self_inner.wfile.write(body.encode("utf-8"))

            def log_message(self_inner, format, *args):
                return

        server = HTTPServer(("127.0.0.1", self.prometheus_port), Handler)
        self._prometheus_server = server

        def serve():
            try:
                server.serve_forever()
            except Exception:
                pass

        t = threading.Thread(target=serve, daemon=True)
        t.start()

    def _start_opentelemetry_sdk(self, otlp_url=None, interval_seconds=None):
        # Best-effort: initialize MeterProvider and TracerProvider with OTLP exporters.
        try:
            # Metrics API and MeterProvider
            from opentelemetry import metrics as ot_metrics
            from opentelemetry.sdk.metrics import MeterProvider
            from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
            # Resource and tracing helpers
            try:
                from opentelemetry.sdk.resources import Resource
                from opentelemetry.semconv.resource import ResourceAttributes
            except Exception:
                Resource = None
                ResourceAttributes = None

            # OTLP metric exporter (try HTTP, fallback to gRPC)
            try:
                from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
            except Exception:
                try:
                    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
                except Exception:
                    OTLPMetricExporter = None

            if OTLPMetricExporter is None:
                print("[OTEL] OTLP metric exporter not available in opentelemetry package")
                return False

            # Build resource with service attributes
            svc_name = os.environ.get('METRICS_SERVICE_NAME', 'research-assistant')
            svc_ver = os.environ.get('METRICS_SERVICE_VERSION')
            svc_env = os.environ.get('METRICS_DEPLOY_ENV', os.environ.get('DEPLOYMENT_ENVIRONMENT', 'development'))
            resource = None
            if Resource is not None and ResourceAttributes is not None:
                try:
                    attrs = {
                        ResourceAttributes.SERVICE_NAME: svc_name,
                        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: svc_env,
                    }
                    if svc_ver:
                        attrs[ResourceAttributes.SERVICE_VERSION] = svc_ver
                    resource = Resource(attributes=attrs)
                except Exception:
                    resource = None

            # Configure metric exporter with endpoint and headers
            metric_exporter_kwargs = {}
            if otlp_url:
                metric_exporter_kwargs['endpoint'] = otlp_url
            hdrs = os.environ.get('METRICS_OTLP_HEADERS')
            if hdrs:
                try:
                    import json as _json
                    metric_exporter_kwargs['headers'] = _json.loads(hdrs)
                except Exception:
                    try:
                        hdict = dict([p.split('=') for p in hdrs.split(';') if '=' in p])
                        metric_exporter_kwargs['headers'] = hdict
                    except Exception:
                        pass
            metric_exporter_kwargs['compression'] = 'gzip'

            exporter = OTLPMetricExporter(**metric_exporter_kwargs) if metric_exporter_kwargs else OTLPMetricExporter()
            reader_kwargs = {}
            if interval_seconds is not None:
                reader_kwargs['export_interval_millis'] = int(float(interval_seconds) * 1000)

            reader = PeriodicExportingMetricReader(exporter, **reader_kwargs)
            provider_kwargs = {}
            if resource is not None:
                provider_kwargs['resource'] = resource
            provider = MeterProvider(metric_readers=[reader], **provider_kwargs)
            try:
                ot_metrics.set_meter_provider(provider)
            except Exception:
                ot_metrics._METER_PROVIDER = provider

            meter = ot_metrics.get_meter(__name__)
            self._otel_instruments = {}

            # Observable callbacks
            def make_token_callback(name):
                def callback(observable):
                    payload = self._latest_payload or {}
                    tt = payload.get('token_tracker', {})
                    try:
                        observable.observe(tt.get(name, 0), {})
                    except Exception:
                        pass
                return callback

            try:
                try:
                    meter.create_observable_gauge("token_total_tokens", make_token_callback('total_tokens'))
                    meter.create_observable_gauge("token_records", make_token_callback('records'))
                    meter.create_observable_gauge("cache_entries", make_token_callback('entries'))
                except Exception:
                    try:
                        meter.register_observable_gauge("token_total_tokens", make_token_callback('total_tokens'))
                        meter.register_observable_gauge("token_records", make_token_callback('records'))
                        meter.register_observable_gauge("cache_entries", make_token_callback('entries'))
                    except Exception:
                        print("[OTEL] Failed to register observable instruments (API mismatch)")

                try:
                    self._otel_instruments['token_counter'] = meter.create_counter("token_counter")
                    self._otel_instruments['cache_writes'] = meter.create_counter("cache_writes")
                    self._otel_instruments['cache_hits'] = meter.create_counter("cache_hits")
                    try:
                        self._otel_instruments['token_histogram'] = meter.create_histogram("token_histogram")
                    except Exception:
                        pass
                except Exception:
                    pass

            except Exception:
                print("[OTEL] Observable instrumentation setup failed:\n", traceback.format_exc())

            # Tracing setup: configure a TracerProvider + BatchSpanProcessor with OTLP exporter
            try:
                from opentelemetry import trace as ot_trace
                from opentelemetry.sdk.trace import TracerProvider
                from opentelemetry.sdk.trace.export import BatchSpanProcessor
                try:
                    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
                except Exception:
                    try:
                        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                    except Exception:
                        OTLPSpanExporter = None

                if OTLPSpanExporter is not None:
                    trace_kwargs = {}
                    if otlp_url:
                        trace_kwargs['endpoint'] = otlp_url
                    if 'headers' in metric_exporter_kwargs:
                        trace_kwargs['headers'] = metric_exporter_kwargs['headers']
                    trace_kwargs['compression'] = 'gzip'
                    trace_kwargs['timeout'] = int(os.environ.get('METRICS_OTLP_TIMEOUT', '10'))

                    span_exporter = OTLPSpanExporter(**trace_kwargs) if trace_kwargs else OTLPSpanExporter()
                    tracer_provider = TracerProvider(resource=resource) if resource is not None else TracerProvider()
                    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
                    try:
                        ot_trace.set_tracer_provider(tracer_provider)
                    except Exception:
                        try:
                            ot_trace._TRACER_PROVIDER = tracer_provider
                        except Exception:
                            pass
            except Exception:
                pass

            print("[OTEL] OpenTelemetry SDK exporter configured")
            return True
        except Exception:
            print("[OTEL] OpenTelemetry SDK not available or failed to initialize")
            return False

    def _export(self, payload):
        if self.exporter == "console":
            self._export_console(payload)
            return

        if self.exporter == "file":
            self._export_file(payload)
            return

        if self.exporter in ("otlp", "OTLP"):
            self._export_otlp(payload)
            return

        if self.exporter in ("prometheus", "prom"):
            # Prometheus server serves the latest payload; ensure it's running
            if not self._prometheus_server:
                try:
                    self._start_prometheus()
                except Exception:
                    print("Failed to start Prometheus server:\n", traceback.format_exc())
            # no-op otherwise; handler will read self._latest_payload
            # update prometheus_client metrics if present
            try:
                if self._prom_registry and self._prom_metrics:
                    tt = payload.get('token_tracker', {})
                    per_tool = tt.get('per_tool', {})
                    # try to attach trace_id as a label if available
                    trace_id = self._get_latest_trace_id()
                    for tool, vals in (per_tool.items() if isinstance(per_tool, dict) else []):
                        try:
                            if trace_id:
                                # provide trace_id as an additional label
                                self._prom_metrics['token_total_tokens'].labels(tool=tool, trace_id=trace_id).set(int(vals.get('tokens_total', 0)))
                                self._prom_metrics['token_requests'].labels(tool=tool, trace_id=trace_id).set(int(vals.get('count', 0)))
                                self._prom_metrics['token_avg'].labels(tool=tool, trace_id=trace_id).set(float(vals.get('avg_tokens', 0)))
                            else:
                                self._prom_metrics['token_total_tokens'].labels(tool=tool).set(int(vals.get('tokens_total', 0)))
                                self._prom_metrics['token_requests'].labels(tool=tool).set(int(vals.get('count', 0)))
                                self._prom_metrics['token_avg'].labels(tool=tool).set(float(vals.get('avg_tokens', 0)))
                        except Exception:
                            pass
                    # If no per-tool metrics were emitted, ensure a default sample exists
                    try:
                        if not per_tool:
                            default_tool = 'unknown'
                            if trace_id:
                                self._prom_metrics['token_total_tokens'].labels(tool=default_tool, trace_id=trace_id).set(int(tt.get('total_tokens', 0)))
                                self._prom_metrics['token_requests'].labels(tool=default_tool, trace_id=trace_id).set(int(tt.get('records', 0)))
                                self._prom_metrics['token_avg'].labels(tool=default_tool, trace_id=trace_id).set(float((tt.get('total_tokens', 0) or 0) / (tt.get('records', 1) or 1)))
                            else:
                                self._prom_metrics['token_total_tokens'].labels(tool=default_tool, trace_id='').set(int(tt.get('total_tokens', 0)))
                                self._prom_metrics['token_requests'].labels(tool=default_tool, trace_id='').set(int(tt.get('records', 0)))
                                self._prom_metrics['token_avg'].labels(tool=default_tool, trace_id='').set(float((tt.get('total_tokens', 0) or 0) / (tt.get('records', 1) or 1)))
                    except Exception:
                        pass
                    c = payload.get('cache', {})
                    try:
                        self._prom_metrics['cache_entries'].set(int(c.get('entries', 0)))
                        self._prom_metrics['cache_writes'].set(int(c.get('writes', 0) or 0))
                        self._prom_metrics['cache_hits'].set(int(c.get('hits', 0) or 0))
                    except Exception:
                        pass
            except Exception:
                pass
            return

        # If OpenTelemetry SDK instruments were created, update counters/histograms
        try:
            if hasattr(self, '_otel_instruments') and self._otel_instruments:
                instr = self._otel_instruments
                tt = payload.get('token_tracker', {})
                c = payload.get('cache', {})
                # counters: add totals (best-effort; OTEL counters are monotonic)
                try:
                    if 'token_counter' in instr:
                        instr['token_counter'].add(int(tt.get('total_tokens', 0)))
                    if 'cache_writes' in instr:
                        instr['cache_writes'].add(int(c.get('writes', 0)))
                    if 'cache_hits' in instr:
                        instr['cache_hits'].add(int(c.get('hits', 0) or 0))
                    if 'token_histogram' in instr:
                        instr['token_histogram'].record(int(tt.get('total_tokens', 0)))
                except Exception:
                    # ignore OTEL emission errors
                    pass
                    # Emit per-request exemplars by recording recent TokenTracker records with attributes
                    try:
                        records = getattr(self.token_tracker, 'records', []) or []
                        # limit to last N records to avoid high cardinality
                        for r in records[-50:]:
                            try:
                                tokens = int(r.get('tokens', 0) or 0)
                                meta = r.get('meta', {}) or {}
                                tool = meta.get('tool', 'unknown')
                                trace_id = meta.get('trace_id')
                                attrs = {}
                                if tool:
                                    attrs['tool'] = tool
                                if trace_id:
                                    attrs['trace_id'] = trace_id
                                # record exemplar values into OTEL histogram/counters if available
                                if 'token_histogram' in instr:
                                    try:
                                        instr['token_histogram'].record(tokens, attrs)
                                    except TypeError:
                                        # some OTEL versions expect different arg order/naming
                                        try:
                                            instr['token_histogram'].record(tokens, attributes=attrs)
                                        except Exception:
                                            pass
                                if 'token_counter' in instr:
                                    try:
                                        instr['token_counter'].add(tokens, attrs)
                                    except TypeError:
                                        try:
                                            instr['token_counter'].add(tokens, attributes=attrs)
                                        except Exception:
                                            pass
                            except Exception:
                                continue
                    except Exception:
                        pass
        except Exception:
            pass

        # unknown exporter: fallback to file
        self._export_file(payload)

    def _run(self):
        while not self._stop_event.is_set():
            start = time.time()
            payload = self._collect()
            try:
                self._export(payload)
            except Exception:
                print("Metrics export failed:\n", traceback.format_exc())

            elapsed = time.time() - start
            to_wait = self.interval - elapsed
            if to_wait > 0:
                self._stop_event.wait(to_wait)

    def start(self, wait_for_first=False):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        # Start prometheus server upfront if requested
        if self.exporter in ("prometheus", "prom"):
            try:
                self._start_prometheus()
            except Exception:
                print("Failed to start Prometheus server:\n", traceback.format_exc())

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        if wait_for_first:
            time.sleep(min(self.interval, 0.1))

    def stop(self, timeout=5):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout)
        if self._prometheus_server:
            try:
                self._prometheus_server.shutdown()
            except Exception:
                pass

    def force_flush(self):
        """Collect and export immediately (synchronous)."""
        payload = self._collect()
        self._export(payload)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()
