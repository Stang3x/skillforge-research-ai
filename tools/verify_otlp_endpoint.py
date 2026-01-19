"""Verify connectivity to an OTLP-like HTTP endpoint by making a best-effort POST of a sample JSON metrics payload.

Usage:
  python tools/verify_otlp_endpoint.py --url https://collector.example/api/v1/metrics

This is a connectivity check; back-end verification of exemplars must be performed in the backend UI.
"""
import argparse
import json
import urllib.request

SAMPLE = {
    "timestamp": "2026-01-01T00:00:00Z",
    "token_tracker": {"total_tokens": 1, "total_cost": 0.0, "records": 1},
    "cache": {"entries": 0}
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', '-u', required=True)
    args = parser.parse_args()
    data = json.dumps(SAMPLE).encode('utf-8')
    req = urllib.request.Request(args.url, data=data, headers={"Content-Type": "application/json"}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            code = resp.getcode()
            print('POST returned', code)
            try:
                body = resp.read().decode('utf-8')
                print('Response body:', body[:1000])
            except Exception:
                pass
    except Exception as e:
        print('POST failed:', repr(e))


if __name__ == '__main__':
    main()
