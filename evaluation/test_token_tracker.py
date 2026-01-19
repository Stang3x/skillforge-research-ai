"""
Unit tests for TokenTracker

Run: python -m pytest evaluation/test_token_tracker.py
"""
import os
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.token_tracker import TokenTracker


def test_record_and_persistence(tmp_path):
    storage = tmp_path / 'tt.json'
    tt = TokenTracker(storage=str(storage), cost_per_1k_tokens=0.01)
    assert tt.summary()['total_tokens'] == 0

    res = tt.record_request('hello world', 'this is a response')
    assert tt.summary()['records'] == 1
    assert tt.total_tokens > 0
    # reload from disk
    tt2 = TokenTracker(storage=str(storage), cost_per_1k_tokens=0.01)
    assert tt2.summary()['records'] == 1


def test_budget_alert(tmp_path):
    storage = tmp_path / 'tt2.json'
    tt = TokenTracker(storage=str(storage), cost_per_1k_tokens=10.0)  # expensive tokens to trigger budget
    tt.set_budget(0.00001)
    r = tt.record_request('a'*100, 'b'*100)
    # Expect alert key when budget exceeded
    assert 'alert' in r or tt.summary()['total_cost'] <= tt.budget


def test_reset(tmp_path):
    storage = tmp_path / 'tt3.json'
    tt = TokenTracker(storage=str(storage))
    tt.record_request('q', 'r')
    assert tt.summary()['records'] == 1
    tt.reset()
    assert tt.summary()['records'] == 0


if __name__ == '__main__':
    test_record_and_persistence(Path('tmp'))
    test_budget_alert(Path('tmp'))
    test_reset(Path('tmp'))
    print('TokenTracker tests passed (smoke)')
