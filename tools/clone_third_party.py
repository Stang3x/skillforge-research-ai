"""Clone configured third-party script collections into reference-repositories/third_party

Usage:
    python tools/clone_third_party.py

This script performs shallow clones of repositories into the recommended local paths.
Run it from the repository root. It prints progress and exits non-zero on error.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

REPOS = [
    ("https://github.com/wasmerio/Python-Scripts.git", "reference-repositories/third_party/wasmerio-Python-Scripts"),
    ("https://github.com/DedSecInside/Awesome-Scripts.git", "reference-repositories/third_party/awesome-scripts-dedsecinside"),
]


def run(cmd: list[str]) -> None:
    print("=>", " ".join(cmd))
    res = subprocess.run(cmd, check=False)
    if res.returncode != 0:
        print(f"Command failed: {res.returncode}")
        sys.exit(res.returncode)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    root = Path.cwd()
    print(f"Working from: {root}")
    for url, dst in REPOS:
        dst_path = Path(dst)
        if dst_path.exists():
            print(f"Skipping existing: {dst_path}")
            continue
        ensure_parent(dst_path)
        cmd = ["git", "clone", "--depth", "1", url, str(dst_path)]
        run(cmd)

    print("All done. Review cloned folders under reference-repositories/third_party/")


if __name__ == "__main__":
    main()
