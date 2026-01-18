# Local testbed for exemplar validation

This folder contains a minimal Docker Compose testbed used by CI to verify exemplars:

- `otel-collector` (OpenTelemetry Collector Contrib) exposing a Prometheus exporter with OpenMetrics support on port `9464`.
- `tempo` (Grafana Tempo) as a simple trace backend.

Quick start (requires Docker and docker-compose or the `docker-compose` Python package):

```bash
# from repo root
docker-compose -f .github/testbed/docker-compose.yml up -d

# wait until collector /metrics is available
curl -H "Accept: application/openmetrics-text" http://localhost:9464/metrics | sed -n '1,120p'

# run the harness against the local collector
python tools/exemplar_harness.py --mode collector --collector-url http://localhost:9464/metrics

# tear down when done
docker-compose -f .github/testbed/docker-compose.yml down -v --remove-orphans
```

Notes
- The CI workflow `/.github/workflows/exemplar-harness.yml` will automatically start this testbed when `METRICS_COLLECTOR_URL` is not provided as a secret.
- The included testbed pins known-good versions; adjust in `docker-compose.yml` if needed.
