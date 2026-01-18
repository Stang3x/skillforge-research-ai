"""Token tracking utilities for per-tool/request token accounting.

Provides a simple JSON-persisted TokenTracker with methods to record
token usage, query totals, and check budgets.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Dict, Optional


class TokenTracker:
    def __init__(self, path: str | Path = "evaluation/token_tracker.json"):
        self.path = Path(path)
        self._lock = threading.Lock()
        self._data: Dict[str, Dict[str, int]] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    raw = json.load(f)
                # ensure ints
                self._data = {k: {kk: int(vv) for kk, vv in v.items()} for k, v in raw.items()}
            except Exception:
                # corrupted file — reset
                self._data = {}
        else:
            self._data = {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def record(self, tool: str, prompt_tokens: int = 0, completion_tokens: int = 0) -> None:
        """Record token usage for a given tool.

        This method is thread-safe and persists to disk on each call.
        """
        if prompt_tokens < 0 or completion_tokens < 0:
            raise ValueError("token counts must be non-negative")

        with self._lock:
            entry = self._data.setdefault(tool, {"prompt": 0, "completion": 0, "total": 0})
            entry["prompt"] += int(prompt_tokens)
            entry["completion"] += int(completion_tokens)
            entry["total"] += int(prompt_tokens) + int(completion_tokens)
            self._save()

    def totals(self, tool: Optional[str] = None) -> Dict[str, int] | int:
        """Return totals for a tool or aggregate total across all tools.

        If `tool` is provided, returns the tool's summary dict. Otherwise
        returns the aggregate total int.
        """
        with self._lock:
            if tool:
                return dict(self._data.get(tool, {"prompt": 0, "completion": 0, "total": 0}))
            # aggregate total
            return sum(v.get("total", 0) for v in self._data.values())

    def budget_exceeded(self, tool: str, budget: int) -> bool:
        """Return True if the given tool's total tokens exceed `budget`."""
        if budget < 0:
            raise ValueError("budget must be non-negative")
        with self._lock:
            return self._data.get(tool, {}).get("total", 0) > int(budget)

    def reset(self) -> None:
        """Reset all counters and persist the empty state."""
        with self._lock:
            self._data = {}
            self._save()


if __name__ == "__main__":
    # simple CLI for debugging
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--path", default=None)
    p.add_argument("--show", action="store_true")
    p.add_argument("--reset", action="store_true")
    args = p.parse_args()
    tracker = TokenTracker(args.path) if args.path else TokenTracker()
    if args.reset:
        tracker.reset()
        print("reset")
    if args.show:
        print(json.dumps(tracker._data, indent=2))
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


from typing import Callable
from dataclasses import dataclass


@dataclass
class MockResponse:
    """Small compatibility helper used by benchmarks to represent token counts."""
    input_tokens: int = 0
    output_tokens: int = 0


class TokenTracker:
    def __init__(self, storage: str = 'evaluation/token_tracker.json', cost_per_1k_tokens: float = 0.002, notifier: Optional[Callable] = None):
        self.storage = Path(storage)
        self.cost_per_1k = float(cost_per_1k_tokens)
        self.records = []
        self.total_tokens = 0
        # Backwards-compatible fields expected by older benchmark code
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.budget = None
        self.notifier = notifier
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
        # Attempt to preserve input/output breakdown where possible
        try:
            self.total_input_tokens += int(pt)
            self.total_output_tokens += int(ct)
        except Exception:
            pass
        self.total_cost += cost
        self._save()

        # budget alert
        if self.budget is not None and self.total_cost > self.budget:
            alert = {'alert': 'budget_exceeded', 'total_cost': self.total_cost}
            if self.notifier:
                try:
                    self.notifier('global', alert)
                except Exception:
                    pass
            return alert
        return {'total_tokens': self.total_tokens, 'total_cost': self.total_cost}

    # Backwards-compatible API: record numeric token counts for a named tool
    def record(self, tool: str, prompt_tokens: int = 0, completion_tokens: int = 0):
        tokens = int(prompt_tokens) + int(completion_tokens)
        cost = tokens / 1000.0 * self.cost_per_1k
        rec = {
            'prompt_tokens': int(prompt_tokens),
            'completion_tokens': int(completion_tokens),
            'tokens': tokens,
            'cost': cost,
            'meta': {'tool': tool},
        }
        self.records.append(rec)
        self.total_tokens += tokens
        # maintain compatibility counters
        try:
            self.total_input_tokens += int(prompt_tokens)
            self.total_output_tokens += int(completion_tokens)
        except Exception:
            pass
        self.total_cost += cost
        self._save()
        if self.budget is not None and self.total_cost > self.budget:
            alert = {'alert': 'budget_exceeded', 'total_cost': self.total_cost}
            if self.notifier:
                try:
                    self.notifier(tool, alert)
                except Exception:
                    pass
            return alert
        return {'total_tokens': self.total_tokens, 'total_cost': self.total_cost}

    def track(self, response, agent: Optional[str] = None):
        """Compatibility shim: accept a MockResponse-like object and record tokens.

        `response` may be an object with `input_tokens` and `output_tokens` attributes
        (the benchmark uses `MockResponse`). We translate that into the internal
        record structure and update totals.
        """
        try:
            in_tok = int(getattr(response, 'input_tokens', 0) or 0)
            out_tok = int(getattr(response, 'output_tokens', 0) or 0)
        except Exception:
            in_tok = 0
            out_tok = 0
        tool_name = agent or (getattr(response, 'agent', None) or 'unknown')
        return self.record(tool_name, in_tok, out_tok)

    def totals(self, tool: Optional[str] = None):
        if tool:
            total = 0
            for r in self.records:
                meta = r.get('meta', {}) if isinstance(r, dict) else {}
                if meta.get('tool') == tool:
                    total += int(r.get('tokens', 0) or 0)
            # return structure matching earlier TokenTracker
            # split into prompt/completion totals where possible
            prompt = sum(int(r.get('prompt_tokens', 0) or 0) for r in self.records if (r.get('meta', {}) or {}).get('tool') == tool)
            completion = sum(int(r.get('completion_tokens', 0) or 0) for r in self.records if (r.get('meta', {}) or {}).get('tool') == tool)
            return {'prompt': prompt, 'completion': completion, 'total': total}
        return int(self.total_tokens)

    def budget_exceeded(self, tool: str, budget: int) -> bool:
        if budget < 0:
            raise ValueError("budget must be non-negative")
        totals = self.totals(tool)
        if isinstance(totals, dict):
            return totals.get('total', 0) > int(budget)
        return totals > int(budget)

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
