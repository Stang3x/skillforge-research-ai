"""Python wrapper to run the PowerShell PSScriptAnalyzer helper safely.

Usage:
  python tools/run_psscriptanalyzer.py --fail-on-error

This wrapper uses `tools/run_command.py` to invoke the PowerShell script using
`pathlib` to avoid Windows backslash escape issues when Python constructs
command arguments.
"""
import argparse
from pathlib import Path
import sys

# Ensure repo root is on sys.path so `import tools.run_command` works when invoked
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.run_command import run_script


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--fail-on-error', action='store_true')
    args = p.parse_args()

    script = Path(__file__).resolve().parents[0] / 'run_psscriptanalyzer.ps1'
    cmd_args = []
    if args.fail_on_error:
        cmd_args.append('-FailOnError')

    try:
        run_script(script, cmd_args, check=True)
    except Exception as e:
        raise SystemExit(1) from e


if __name__ == '__main__':
    main()
