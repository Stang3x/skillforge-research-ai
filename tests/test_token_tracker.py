import os
from pathlib import Path

from evaluation.token_tracker import TokenTracker


def test_record_and_totals(tmp_path):
    p = tmp_path / "tt.json"
    tracker = TokenTracker(p)
    tracker.record("toolA", prompt_tokens=10, completion_tokens=5)
    tracker.record("toolA", prompt_tokens=3, completion_tokens=2)
    totals = tracker.totals("toolA")
    assert totals["prompt"] == 13
    assert totals["completion"] == 7
    assert totals["total"] == 20

    # aggregate
    tracker.record("toolB", prompt_tokens=1, completion_tokens=1)
    assert tracker.totals() == 22


def test_budget_and_persistence(tmp_path):
    p = tmp_path / "tt2.json"
    tracker = TokenTracker(p)
    tracker.record("toolX", prompt_tokens=50, completion_tokens=0)
    assert not tracker.budget_exceeded("toolX", 100)
    assert tracker.budget_exceeded("toolX", 40)

    # reload and ensure persistence
    t2 = TokenTracker(p)
    assert t2.totals("toolX")["total"] == 50
