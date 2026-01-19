# Exemplars & Trace-Metric Correlation — Notes and Actions

Sources reviewed:
- Vincent Behar, "Using Prometheus Exemplars to jump from metrics to traces in Grafana" (Medium)
- OpenTelemetry Collector issue: `exporter/prometheus` exemplars not exposed (#38878)
- Eric D. Schabell, "Hands-on Guide... Linking Metrics to Traces with Exemplars (part 2)"

Key findings (concise):

- Exemplars are special annotations attached to metric data points that carry example labels (commonly `trace_id`) and a timestamp/value. They enable jumping from a metric time series to the correlating trace.

- OpenMetrics vs Prometheus text format: exemplars are only supported in the OpenMetrics exposition format. Clients or servers must expose metrics in OpenMetrics (Accept: `application/openmetrics-text`) for exemplars to appear. Prometheus scrapers typically request OpenMetrics when configured.

- Prometheus server: exemplar storage is an opt-in feature in some builds; the `--enable-feature=exemplar-storage` flag (or using a Prometheus build that includes exemplar support) is required for storing and displaying exemplars. Grafana visualizes exemplars if Prometheus provides them and the Grafana data source is configured for exemplars.

- Instrumentation libraries: language client support varies. For Go, client_golang added exemplar APIs in v1.4.0; for Python there are multiple patterns (prometheus_client extensions, `prometheus-flask-exporter` and manual exemplar arguments). Key point: attach exemplar *to the metric*, not as an ordinary label (to avoid cardinality explosion).

- OpenTelemetry Collector behavior: the Collector can receive exemplars from instrumented apps (logs may show exemplars) but historically there have been issues where the `exporter/prometheus` did not expose exemplars on `/metrics` (see issue #38878). Findings from that issue:
  - Exemplars are time-sensitive and often visible only while a request/span is in-flight; collector/exporter must scrape while exemplar is present.
  - The `Accept: application/openmetrics-text` header is required to see exemplar annotations in the collector's `/metrics` output.
  - There have been configuration and implementation limitations across collector and Prometheus exporter versions; some `enable_exemplars` flags caused crashes on certain collector versions.

- Grafana: to link exemplars to a trace store (Tempo), configure the Prometheus datasource exemplar settings (`exemplarTraceIdDestinations`) and use Time series panels with Exemplars enabled. Grafana will build links to the trace backend (Tempo) using the exemplar's trace id and configured destination.

Practical recommendations for our project (priority and short actions):

1. Emit exemplars from the app/agent when possible (low cardinality):
   - Don’t add `trace_id` as a normal metric label. Instead emit exemplars on candidate metrics (histograms, counters) via the client library's exemplar API when available.
   - For Python, prefer explicit exemplar APIs (e.g., `inc(..., exemplar={...})` or library-specific `ObserveWithExemplar`) from `prometheus_client`/`prometheus-flask-exporter` or via the OpenTelemetry metrics SDK when exemplars are supported.

2. Use OpenMetrics exposition and ensure scrapers request it:
   - When exposing metrics through an intermediary (OpenTelemetry Collector), make sure the Prometheus exporter is configured with `enable_open_metrics: true` so the `/metrics` endpoint can return OpenMetrics with exemplar annotations.
   - For manual testing, use `curl -H "Accept: application/openmetrics-text" http://host:port/metrics` to verify exemplars.

3. Collector & Prometheus setup for CI/local testing:
   - Use a Collector version and Prometheus build that support exemplars; enable exemplar storage in Prometheus builds that require it (`--enable-feature=exemplar-storage`).
   - Set exemplar sampling env vars during tests for visibility: `OTEL_EXEMPLARS_SAMPLING_PROBABILITY=1.0` and `OTEL_EXEMPLAR_FILTER=always_on` (only for debug/test).
   - Be aware exemplars are short-lived — ensure Prometheus scrapes while the exemplar is in-flight.

4. Grafana configuration for trace linking:
   - Configure Prometheus datasource `exemplarTraceIdDestinations` mapping the exemplar key (e.g., `TraceID`) to the Tempo datasource UID.
   - Use Time series panels and enable Exemplars in the panel options.

5. Collector exporter caveats & our exporter code:
   - The OTEL Collector `exporter/prometheus` historically had issues exposing exemplars — validate on the exact collector version used in CI. If collector-path proves unreliable, consider alternative flows:
     - Send metrics + exemplars directly to Prometheus (OTLP remote write/remote write receiver) or
     - Have the instrumented app expose OpenMetrics with exemplars directly (app-level HTTP /metrics) and let Prometheus scrape the app.

6. Test harness & CI additions (short list):
   - Add a small exemplar validation harness that:
     - Emits a metric with exemplar and a trace/span (manual instrumentation),
     - Configures OTEL_EXEMPLARS_SAMPLING_PROBABILITY=1.0 for deterministic testing,
     - Scrapes the collector `/metrics` with Accept: application/openmetrics-text and asserts exemplar annotation is present,
     - Optionally validates Grafana/Tempo linking in an integration environment.

Storage / learning location:
- Saved this summary to `documentation/exemplars_integration.md` for future reference and actionable steps.
- Recommended next steps: add the small exemplar harness to `tools/` (I can implement) and wire it into CI with a configurable OTLP/Tempo endpoint to validate exemplars in a real backend.

References & commands used during testing:
- `curl -H "Accept: application/openmetrics-text" http://collector:9464/metrics` — request OpenMetrics to view exemplars.
- Env vars for deterministic examples: `OTEL_EXEMPLARS_SAMPLING_PROBABILITY=1.0` and `OTEL_EXEMPLAR_FILTER=always_on`.

Notes: exemplar behavior and tooling have evolved; always validate the exact Collector and Prometheus versions used in CI and production. Some flags (e.g., `enable_exemplars`) may be unstable on older collector versions — prefer documented stable configuration and fallback to instrumenting the app to expose OpenMetrics directly if necessary.

OTLP exporter & tracer best-practices (practical)
------------------------------------------------

- Use HTTP OTLP exporters with authentication headers when sending to vendor backends (Grafana Cloud, Honeycomb, Elastic). Provide `headers` and prefer HTTP/protobuf endpoints (port 4318) unless your backend requires gRPC.
- Enable compression and reasonable timeouts to avoid stalls and save bandwidth. Example exporter kwargs (Python style): `compression='gzip'`, `timeout=10`.
- Configure a `Resource` for your service (`service.name`, `service.version`, `deployment.environment`) so exemplars and traces are easily attributable in backends.
- Use a `BatchSpanProcessor` for spans; it reduces pressure on network and encourages exemplar visibility when paired with appropriate exemplar sampling.

Minimal Python example (conceptual)

```py
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider = TracerProvider(resource=...)  # set Resource attributes
exporter = OTLPSpanExporter(endpoint=ENDPOINT, headers=HEADERS, compression='gzip', timeout=10)
provider.add_span_processor(BatchSpanProcessor(exporter))
```

This aligns with the `working example.txt` snippet in `documentation/` which demonstrates authenticated OTLP HTTP exporter usage.

Known-good setups & verification
--------------------------------

- Recommendation: prefer recent stable releases of the OpenTelemetry Collector (contrib) and Prometheus. If you cannot upgrade, validate exemplar support using the manual checks below before relying on CI assertions.

- How to verify a Prometheus build supports exemplar storage:
   - If you control the Prometheus process, start it with exemplar storage enabled (example flag for custom builds): `--enable-feature=exemplar-storage`.
   - Verify by scraping a test endpoint that emits OpenMetrics exemplars (see `tools/exemplar_harness.py`). Use:

```bash
curl -H "Accept: application/openmetrics-text" http://<host>:<port>/metrics | sed -n '1,120p'
```

   - Look for exemplar annotations on samples such as: `# {trace_id="..."}` after a sample value.

- How to verify the OpenTelemetry Collector's Prometheus exporter will expose exemplars:
   - Ensure the Collector's Prometheus exporter is configured to emit OpenMetrics (e.g., `enable_open_metrics: true` in exporter config) and that the Collector version includes exemplar handling.
   - For local debugging, point `tools/exemplar_harness.py --mode collector --collector-url http://localhost:9464/metrics` at your collector and inspect the output.

- CI notes:
   - In CI, secrets are not available to pull-request workflows from forked repos. Configure a protected branch (e.g., `develop`) and set the `METRICS_COLLECTOR_URL` secret in repository settings to enable collector-mode validation for trusted runs.
   - If the collector-mode check fails in CI, consult the uploaded `harness-collector-log` artifact to investigate timing/configuration issues.

   Suggested (known-good) versions
   --------------------------------

   - OpenTelemetry Collector (contrib): `otel/opentelemetry-collector-contrib:0.81.0` or later
   - Prometheus: `prom/prometheus:2.44.0` or later
   - Grafana Tempo: `grafana/tempo:1.6.0` (for trace storage and linking)

   These are suggested starting points used by the included local CI testbed (`.github/testbed/docker-compose.yml` and `.github/testbed/otel-collector-config.yaml`). If you pin other versions, validate exemplar support with `tools/exemplar_harness.py`.

