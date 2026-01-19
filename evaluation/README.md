# Evaluation - Token Tracking

This folder contains the `TokenTracker` utility used to record per-request token usage,
calculate approximate cost, and emit budget alerts.

Usage
-----

Basic programmatic usage:

```python
from evaluation.token_tracker import TokenTracker

# optional notifier: use evaluation.alerts.notifier_from_env(slack_url)
tracker = TokenTracker(storage='evaluation/token_tracker.json')
tracker.record('search_tool', prompt_tokens=100, completion_tokens=50)
print(tracker.totals('search_tool'))
```

Recording from production agents
--------------------------------

In your production agent flow, call `tracker.record_request(prompt, completion, meta={})`
or `tracker.record(tool, prompt_tokens, completion_tokens)` after each request/response pair.

Examples and integration points are provided in `research-assistant/researchassistant.py`.

Alerts
------

You can pass an optional notifier (callable) when constructing the `TokenTracker`.
The helper `evaluation.alerts.notifier_from_env(slack_webhook_url)` builds a notifier
that posts to Slack when a budget is exceeded, or falls back to console logging.

CI & Secrets
------------

Set `SLACK_WEBHOOK_URL` (and optionally `METRICS_COLLECTOR_URL`) as repository secrets
and the CI workflow will expose them to the test job environment so alerting can run
in CI test scenarios.
