Metrics Exporter (research-assistant)

This repository includes a lightweight `PeriodicMetricsExporter` to periodically collect and export local metrics (e.g. `TokenTracker` and cache stats).

Environment variables

- `METRICS_EXPORTER_ENABLED` (default: `0`) — set to `1` or `true` to enable the exporter. In `LOCAL_TEST` mode the exporter is enabled by default unless explicitly set.
- `METRICS_EXPORT_INTERVAL` (default: `60`) — export interval in seconds. In `LOCAL_TEST` default is `1` second.
- `METRICS_EXPORT_TARGET` (default: `console`) — `console` or `file`.
- `METRICS_EXPORT_FILE` (default: `metrics_export.jsonl` under the project root) — file path used when `METRICS_EXPORT_TARGET=file`.

OTLP & Prometheus support

- `METRICS_EXPORT_TARGET=otlp` — exporter will attempt an HTTP POST of JSON payloads to `METRICS_OTLP_URL`.
- `METRICS_OTLP_URL` — URL to POST metrics JSON to (best-effort; no OTLP protobuf encoding).
- `METRICS_EXPORT_TARGET=prometheus` — exporter will start a small HTTP server on `METRICS_PROM_PORT` and expose `/metrics` in Prometheus text format.
- `METRICS_PROM_PORT` — port for the Prometheus endpoint (default: 9091 for local test).

Quick local test

1. Enable local test and run the assistant (on Windows PowerShell):

```powershell
$env:LOCAL_TEST = "1"
$env:METRICS_EXPORTER_ENABLED = "1"
python -m research_assistant.research_assistant
```

2. By default in `LOCAL_TEST` the exporter will write to `metrics_export_local.jsonl` in the project root every 1s. You can change the interval or target via env vars above.

Notes

- The exporter is opt-in for production runs; use the environment variables to control behavior.
- The exporter is intentionally simple (console or newline-delimited JSON file). It also supports Prometheus and OTLP-like HTTP pushes as described above.

Examples

- Start a Prometheus endpoint on the default local port:

```powershell
$env:LOCAL_TEST = "1"
$env:METRICS_EXPORTER_ENABLED = "1"
$env:METRICS_EXPORT_TARGET = "prometheus"
python -m research_assistant.research_assistant
```

- Post metrics to a generic HTTP collector (OTLP-like):

```powershell
$env:LOCAL_TEST = "1"
$env:METRICS_EXPORTER_ENABLED = "1"
$env:METRICS_EXPORT_TARGET = "otlp"
$env:METRICS_OTLP_URL = "https://example-collector.local/metrics"
python -m research_assistant.research_assistant
```

Demo script notes

- The included demo `tools/run_local_metrics_demo.py` writes newline-delimited JSON to a file by default. To also start a Prometheus `/metrics` endpoint for scraping, run the demo with `--prometheus` (or `-p`). Use `--duration` to extend how long the demo runs so you have time to scrape.

Example:

```powershell
python tools/run_local_metrics_demo.py --prometheus --duration 10
```

OTLP / Exemplars

- To enable exemplars and tracing-backed correlation, install the OpenTelemetry extras from `requirements-otel.txt` and set `METRICS_EXPORT_TARGET=opentelemetry` or `METRICS_OTLP_URL` to point at your collector. The exporter will attempt to configure both a Metrics `MeterProvider` and a Tracing `TracerProvider` so that `TokenTracker` spans produce `trace_id` values that are attached to metrics records.

- Quick connectivity check to your collector (best-effort JSON POST):

```bash
python tools/verify_otlp_endpoint.py --url https://your-collector.example/v1/metrics
```

- Note: whether exemplars are visible depends on your collector/backend. For Prometheus exemplars, route metrics through an OpenTelemetry Collector configured to export to Prometheus or your backend of choice.

Opentelemetry Python SDK integration

If you prefer to use the official OpenTelemetry Python SDK and exporters, install the optional requirements:

```powershell
python -m pip install -r ../requirements-otel.txt
```

Then set `METRICS_EXPORT_TARGET=opentelemetry` and `METRICS_OTLP_URL` to your collector. The runtime will attempt to configure a `MeterProvider` and PeriodicExportingMetricReader using the installed OTLP exporter. If the opentelemetry packages are not installed or the SDK API differs, the code will fall back to the built-in, dependency-free exporters.
