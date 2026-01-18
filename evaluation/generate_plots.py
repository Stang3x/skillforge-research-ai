"""
Generate PNG plots from evaluation JSON reports.
Creates:
 - evaluation/reports/plots/cold_vs_warm_time.png
 - evaluation/reports/plots/tokens_bar.png

Run: python evaluation/generate_plots.py
"""
from pathlib import Path
import json
import statistics

REPORT_DIR = Path(__file__).resolve().parents[0] / 'reports'
PLOTS_DIR = REPORT_DIR / 'plots'
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# Collect available report files
reports = list(REPORT_DIR.glob('benchmark*_report*.json'))
if not reports:
    print('No benchmark report JSONs found in', REPORT_DIR)
    raise SystemExit(1)

# Merge results from all reports (use latest if duplicate queries)
all_results = []
for r in reports:
    with open(r, 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_results.extend(data.get('results', []))

# Aggregate per-query cold and warm times
queries = [item['query'] for item in all_results]
cold_times = [item['cold']['time_s'] for item in all_results]
# warm may have avg_time_s
warm_times = [item['warm'].get('avg_time_s', item['warm'].get('time_s', 0)) for item in all_results]
input_tokens = [item['cold']['input_tokens'] + item['warm'].get('input_tokens', 0) for item in all_results]
output_tokens = [item['cold']['output_tokens'] + item['warm'].get('output_tokens', 0) for item in all_results]

# Lazy import matplotlib (installed separately)
try:
    import matplotlib.pyplot as plt
except Exception as e:
    print('matplotlib not available:', e)
    raise

# Plot 1: cold vs warm times (top 20 by cold time)
pairs = list(zip(queries, cold_times, warm_times))
# sort by cold times desc
pairs_sorted = sorted(pairs, key=lambda x: x[1], reverse=True)[:20]
labels = [p[0][:40] for p in pairs_sorted]
cold = [p[1] for p in pairs_sorted]
warm = [p[2] for p in pairs_sorted]

x = range(len(labels))
plt.figure(figsize=(12,6))
plt.bar(x, cold, width=0.4, label='cold_time_s')
plt.bar([i+0.4 for i in x], warm, width=0.4, label='warm_time_s')
plt.xticks([i+0.2 for i in x], labels, rotation=45, ha='right')
plt.ylabel('Seconds')
plt.title('Top 20 Queries: Cold vs Warm Time')
plt.legend()
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'cold_vs_warm_time.png')
plt.close()

# Plot 2: tokens (top 20 by input_tokens)
pairs_tok = list(zip(queries, input_tokens, output_tokens))
pairs_tok_sorted = sorted(pairs_tok, key=lambda x: x[1], reverse=True)[:20]
labels2 = [p[0][:40] for p in pairs_tok_sorted]
inputs = [p[1] for p in pairs_tok_sorted]
outputs = [p[2] for p in pairs_tok_sorted]

x = range(len(labels2))
plt.figure(figsize=(12,6))
plt.bar(x, inputs, width=0.4, label='input_tokens')
plt.bar([i+0.4 for i in x], outputs, width=0.4, label='output_tokens')
plt.xticks([i+0.2 for i in x], labels2, rotation=45, ha='right')
plt.ylabel('Tokens')
plt.title('Top 20 Queries: Token Usage')
plt.legend()
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'tokens_bar.png')
plt.close()

print('Saved plots to', PLOTS_DIR)
