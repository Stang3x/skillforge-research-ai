"""Smoke test for PeriodicMetricsExporter.

This script runs a short export cycle and verifies that the exporter writes output.
"""
import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from evaluation.metrics_exporter import PeriodicMetricsExporter
from evaluation.token_tracker import TokenTracker


def run_smoke():
    out_file = os.path.join(os.path.dirname(__file__), "test_metrics_output.jsonl")
    # remove old file
    try:
        os.remove(out_file)
    except Exception:
        pass

    tt = TokenTracker(storage=os.path.join(os.path.dirname(__file__), "token_tracker_test.json"))
    # record a sample request to ensure summary has content
    tt.record_request("hello world", "hi")

    exporter = PeriodicMetricsExporter(token_tracker=tt, cache=None, interval_seconds=1, exporter="file", filename=out_file)
    exporter.start()
    try:
        # let it run a few cycles
        time.sleep(3)
    finally:
        exporter.stop()

    # verify file was written
    if not os.path.exists(out_file):
        print("FAILED: metrics output file not found", out_file)
        raise SystemExit(1)

    with open(out_file, "r", encoding="utf-8") as fh:
        lines = [l for l in fh.readlines() if l.strip()]

    if len(lines) < 1:
        print("FAILED: no metrics lines written")
        raise SystemExit(1)

    print("OK: wrote {} metric lines to {}".format(len(lines), out_file))


if __name__ == "__main__":
    run_smoke()
