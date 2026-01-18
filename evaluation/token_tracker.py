"""
TokenTracker: simple per-request token and cost tracking for evaluation.

Features:
- record_request(prompt, completion) with approximate token counts
- cumulative totals, cost calculation, budget alerts
- persistence to JSON file
"""
import json
from pathlib import Path
from typing import Optional
try:
    from opentelemetry import trace as _otel_trace
    _OTEL_TRACER = _otel_trace.get_tracer(__name__)
except Exception:
    _otel_trace = None
    _OTEL_TRACER = None


class TokenTracker:
    def __init__(self, storage: str = 'evaluation/token_tracker.json', cost_per_1k_tokens: float = 0.002):
        self.storage = Path(storage)
        self.cost_per_1k = float(cost_per_1k_tokens)
        self.records = []
        self.total_tokens = 0
        self.total_cost = 0.0
        self.budget = None
        self._load()

    def _load(self):
        if self.storage.exists():
            try:
                data = json.loads(self.storage.read_text())
                self.records = data.get('records', [])
                self.total_tokens = data.get('total_tokens', 0)
                self.total_cost = data.get('total_cost', 0.0)
                self.budget = data.get('budget')
            except Exception:
                self.records = []
                self.total_tokens = 0
                self.total_cost = 0.0

    def _save(self):
        try:
            self.storage.parent.mkdir(parents=True, exist_ok=True)
            self.storage.write_text(json.dumps({
                'records': self.records,
                'total_tokens': self.total_tokens,
                'total_cost': self.total_cost,
                'budget': self.budget,
            }))
        except Exception:
            pass

    def estimate_tokens(self, text: Optional[str]) -> int:
        if not text:
            return 0
        # rough estimate: 1 token ~= 0.75 words -> tokens = words / 0.75
        words = len(text.split())
        tokens = int(max(1, round(words / 0.75)))
        return tokens

    def record_request(self, prompt: str, completion: str, meta: Optional[dict] = None):
        pt = self.estimate_tokens(prompt)
        ct = self.estimate_tokens(completion)
        tokens = pt + ct
        cost = tokens / 1000.0 * self.cost_per_1k
        # If OpenTelemetry tracer available, wrap the request in a span and capture trace_id
        record_meta = dict(meta or {})
        if _OTEL_TRACER is not None:
            try:
                with _OTEL_TRACER.start_as_current_span("TokenTracker.record_request") as span:
                    ctx = span.get_span_context()
                    if ctx and hasattr(ctx, 'trace_id'):
                        # trace_id is an integer; format as hex
                        record_meta['trace_id'] = format(ctx.trace_id, '032x')
            except Exception:
                # fallback: continue without trace id
                pass

        rec = {
            'prompt_tokens': pt,
            'completion_tokens': ct,
            'tokens': tokens,
            'cost': cost,
            'meta': record_meta,
        }
        self.records.append(rec)
        self.total_tokens += tokens
        self.total_cost += cost
        self._save()

        # budget alert
        if self.budget is not None and self.total_cost > self.budget:
            return {'alert': 'budget_exceeded', 'total_cost': self.total_cost}
        return {'total_tokens': self.total_tokens, 'total_cost': self.total_cost}

    def set_budget(self, amount: float):
        self.budget = float(amount)
        self._save()

    def reset(self):
        self.records = []
        self.total_tokens = 0
        self.total_cost = 0.0
        self._save()

    def summary(self):
        return {
            'total_tokens': self.total_tokens,
            'total_cost': round(self.total_cost, 6),
            'records': len(self.records),
            'budget': self.budget,
        }

    def per_tool_summary(self):
        """Return derived per-tool statistics: count, tokens_total, avg_tokens."""
        try:
            per_tool = {}
            for r in self.records:
                meta = r.get('meta', {}) if isinstance(r, dict) else {}
                tool = meta.get('tool', 'unknown')
                entry = per_tool.setdefault(tool, {'count': 0, 'tokens_total': 0})
                entry['count'] += 1
                entry['tokens_total'] += int(r.get('tokens', 0) or 0)
            for k, v in per_tool.items():
                v['avg_tokens'] = (v['tokens_total'] / v['count']) if v['count'] else 0
            return per_tool
        except Exception:
            return {}


if __name__ == '__main__':
    # quick smoke test
    t = TokenTracker()
    print('Initial:', t.summary())
    res = t.record_request('What is AI?', 'AI stands for artificial intelligence.')
    print('After one request:', t.summary(), res)
