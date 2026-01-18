"""Simple demo: rename files by replacing spaces with underscores.

Usage:
    python tools/demo_file_renamer.py /path/to/dir
"""
from __future__ import annotations
from pathlib import Path
import sys


def rename_spaces(path: Path) -> None:
    for p in path.iterdir():
        if p.is_file():
            new_name = p.name.replace(' ', '_')
            if new_name != p.name:
                p.rename(p.with_name(new_name))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python tools/demo_file_renamer.py <dir>')
        raise SystemExit(2)
    d = Path(sys.argv[1]).expanduser().resolve()
    if not d.exists() or not d.is_dir():
        print('Directory not found:', d)
        raise SystemExit(2)
    rename_spaces(d)
    print('Renamed files in', d)
