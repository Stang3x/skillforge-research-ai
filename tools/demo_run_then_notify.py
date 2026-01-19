"""Demo: run a long task and print a simple notification (console-only).

Usage:
    python tools/demo_run_then_notify.py --duration 10

This is intentionally minimal and avoids external notification services.
"""
from __future__ import annotations
import time
import argparse


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--duration', type=int, default=5, help='seconds to sleep')
    args = p.parse_args()
    print('Starting long task...')
    time.sleep(args.duration)
    print('Task complete — notification:')
    print(f'[NOTIFY] Completed long task after {args.duration} seconds')


if __name__ == '__main__':
    main()
