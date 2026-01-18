"""Test script to exercise the OpenTelemetry SDK integration in metrics_exporter.

Creates a PeriodicMetricsExporter and attempts to initialize the OpenTelemetry SDK
integration path. Prints results and installed versions if available.
"""
import os
import sys
import importlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from evaluation.metrics_exporter import PeriodicMetricsExporter


def print_pkg_version(pkg_name):
    try:
        mod = importlib.import_module(pkg_name)
        v = getattr(mod, '__version__', None)
        print(f"{pkg_name} version: {v}")
    except Exception:
        print(f"{pkg_name} not installed or failed to import")


def run_test():
    print("Detecting installed opentelemetry packages:")
    for pkg in ("opentelemetry", "opentelemetry.sdk", "opentelemetry.sdk.metrics", "opentelemetry.exporter.otlp", "opentelemetry.exporter.prometheus"):
        print_pkg_version(pkg)

    exporter = PeriodicMetricsExporter(interval_seconds=1, exporter=os.getenv('METRICS_EXPORT_TARGET', 'opentelemetry'))
    otlp_url = os.getenv('METRICS_OTLP_URL')
    ok = exporter._start_opentelemetry_sdk(otlp_url=otlp_url, interval_seconds=1)
    print("_start_opentelemetry_sdk returned:", ok)


if __name__ == '__main__':
    run_test()
