"""Simple demo: organize files in a directory into extension-based folders.

Usage:
    python tools/demo_file_organizer.py /path/to/dir

Safe demo using only the standard library.
"""
from __future__ import annotations
import shutil
from pathlib import Path
import sys


def organize(path: Path) -> None:
    for p in path.iterdir():
        if p.is_file():
            ext = p.suffix.lower().lstrip('.') or 'noext'
            dst = path / ext
            dst.mkdir(exist_ok=True)
            target = dst / p.name
            shutil.move(str(p), str(target))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python tools/demo_file_organizer.py <dir>')
        raise SystemExit(2)
    d = Path(sys.argv[1]).expanduser().resolve()
    if not d.exists() or not d.is_dir():
        print('Directory not found:', d)
        raise SystemExit(2)
    organize(d)
    print('Organized files under', d)
