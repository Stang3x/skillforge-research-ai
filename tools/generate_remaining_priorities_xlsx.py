from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from datetime import datetime
from datetime import timedelta
import csv

OUT = "remaining_priorities.xlsx"

headers = [
    "Rank",
    "Task",
    "Description",
    "Area",
    "Priority",
    "Estimated Effort (days)",
    "ETA (date)",
    "Status",
    "Next Action",
    "Owner",
]

rows = [
    [1, "Verify exemplars in backend", "Validate exemplar emission and trace correlation by configuring METRICS_OTLP_URL to a collector and verifying exemplars.", "Telemetry/OTEL", "High", 2, "Pending", "Provide OTLP collector endpoint and run CI", "Dev/Infra"],
    [2, "Full OTLP protobuf exporter path", "Implement non-SDK OTLP protobuf encoding or ensure SDK path reliably used in CI.", "Telemetry/OTLP", "High", 5, "In Progress", "Decide SDK vs direct encoder; implement chosen path", "Dev"],
    [3, "Prometheus metrics labels and exemplars", "Ensure metrics include trace_id labels when available and exemplars emitted for request-level metrics.", "Telemetry/Prometheus", "High", 3, "In Progress", "Exercise with collector and adjust exporter", "Dev"],
    [4, "Convert example workflow to reusable workflow", "Refactor `.github/workflows/prometheus-scrape-example.yml` into a reusable workflow callable by other repos.", "CI", "Medium", 2, "Pending", "Create reusable workflow and update docs", "Dev/Ops"],
    [5, "Tighten CI assertions", "Add stricter assertions for labeled metrics and trace_id presence in CI tests.", "CI/Tests", "High", 1, "Pending", "Add checks and run CI with METRICS_OTLP_URL", "QA/Dev"],
    [6, "OTEL SDK initialization hardening", "Finalize `_start_opentelemetry_sdk` fallback logic and test across OTEL versions.", "Telemetry/OTEL", "Medium", 3, "In Progress", "Add unit tests and smoke runs across versions", "Dev"],
    [7, "Expose persisted metrics for long-term analysis", "Ship JSONL artifacts to an artifacts store or S3 for historical analysis.", "Observability", "Medium", 2, "Pending", "Add CI upload + retention policy", "Ops"],
    [8, "TokenTracker integration coverage", "Extend TokenTracker integration across all agent tool calls and add per-tool budgets and alerts.", "Agent/TokenTracker", "High", 4, "Partially Done", "Audit agent wrappers and add missing hooks", "Dev"],
    [9, "Performance benchmarks for cache", "Run larger scale benchmarks and report latency/throughput tradeoffs for different cache sizes and TTLs.", "Caching/Perf", "Medium", 3, "Pending", "Run `tools/cache_benchmark.py` with datasets and collect results", "Perf"],
    [10, "Add production OTLP config docs", "Document required env vars (`METRICS_OTLP_URL`, headers, timeouts) and secure secret handling.", "Docs/Onboarding", "Medium", 1, "Pending", "Draft README and examples", "Docs"],
    [11, "Reusable exemplar validation harness", "Create a small harness that sends synthetic token records and validates exemplars appear in backend.", "Telemetry/Test", "Low", 2, "Pending", "Implement harness and CI job", "QA"],
    [12, "Alerting for token budget breaches", "Add alerts when TokenTracker reports budget exceed or anomalous token growth.", "Ops/Monitoring", "Medium", 3, "Pending", "Wire metrics to alerting rules", "Ops"],
]

wb = Workbook()
ws = wb.active
ws.title = "Remaining Priorities"

# write header
for c, h in enumerate(headers, start=1):
    ws.cell(row=1, column=c, value=h)

for r_idx, row in enumerate(rows, start=2):
    for c_idx, val in enumerate(row, start=1):
        ws.cell(row=r_idx, column=c_idx, value=val)
    # compute ETA date from estimated effort (days) if present
    try:
        effort = int(row[5] or 0)
        eta = (datetime.utcnow() + timedelta(days=effort)).date().isoformat()
    except Exception:
        eta = ''
    ws.cell(row=r_idx, column=len(row) + 1, value=eta)

# adjust column widths
for i, col in enumerate(headers, start=1):
    ws.column_dimensions[get_column_letter(i)].width = max(15, len(col) + 2)

# add generation timestamp
ws.cell(row=len(rows) + 3, column=1, value=f"Generated: {datetime.utcnow().isoformat()}Z")

wb.save(OUT)
print(f"Wrote {OUT}")

# also export CSV with ETA column
CSV_OUT = "remaining_priorities.csv"
with open(CSV_OUT, 'w', newline='', encoding='utf-8') as csvfh:
    writer = csv.writer(csvfh)
    writer.writerow(headers)
    for row in rows:
        try:
            effort = int(row[5] or 0)
            eta = (datetime.utcnow() + timedelta(days=effort)).date().isoformat()
        except Exception:
            eta = ''
        writer.writerow(list(row) + [eta])

print(f"Wrote {CSV_OUT}")
