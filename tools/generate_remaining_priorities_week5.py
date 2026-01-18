from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
import csv

OUT = "remaining_priorities_week5.xlsx"

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
    [1, "Multi-agent orchestration", "Finalize orchestrator and agent interaction flows.", "Orchestration", "High", 5, "Pending", "Integrate orchestrator into research-assistant", "Dev"],
    [2, "Memory system: knowledge graph", "Implement knowledge-graph based memory and APIs.", "Memory", "High", 6, "Pending", "Prototype memory.graph and connectors", "Dev"],
    [3, "Production OTLP config + secrets", "Document and template production OTLP exporter configs and secret handling.", "Ops", "High", 2, "Pending", "Draft README and example env files", "Ops"],
    [4, "Finalize exemplars backend verification", "Complete CI collector verification and document results.", "Telemetry", "High", 2, "In Progress", "Run CI with METRICS_COLLECTOR_URL", "Dev/Infra"],
    [5, "TokenTracker per-tool budgets", "Add per-tool budget alerts and dashboards.", "Observability", "Medium", 3, "Pending", "Add alert rules and dashboards", "Ops/Dev"],
    [6, "Cache performance scale tests", "Run large-scale cache benchmarks and produce report.", "Caching", "Medium", 4, "Pending", "Run `tools/cache_benchmark.py`", "Perf"],
]

wb = Workbook()
ws = wb.active
ws.title = "Week5 Priorities"

for c, h in enumerate(headers, start=1):
    ws.cell(row=1, column=c, value=h)

for r_idx, row in enumerate(rows, start=2):
    for c_idx, val in enumerate(row, start=1):
        ws.cell(row=r_idx, column=c_idx, value=val)
    try:
        effort = int(row[5] or 0)
        eta = (datetime.utcnow() + timedelta(days=effort)).date().isoformat()
    except Exception:
        eta = ''
    ws.cell(row=r_idx, column=len(row) + 1, value=eta)

for i, col in enumerate(headers, start=1):
    ws.column_dimensions[get_column_letter(i)].width = max(15, len(col) + 2)

ws.cell(row=len(rows) + 3, column=1, value=f"Generated: {datetime.utcnow().isoformat()}Z")

wb.save(OUT)
print(f"Wrote {OUT}")

CSV_OUT = "remaining_priorities_week5.csv"
import csv as _csv
with open(CSV_OUT, 'w', newline='', encoding='utf-8') as csvfh:
    writer = _csv.writer(csvfh)
    writer.writerow(headers)
    for row in rows:
        try:
            effort = int(row[5] or 0)
            eta = (datetime.utcnow() + timedelta(days=effort)).date().isoformat()
        except Exception:
            eta = ''
        writer.writerow(list(row) + [eta])

print(f"Wrote {CSV_OUT}")
