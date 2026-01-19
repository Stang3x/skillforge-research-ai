from pathlib import Path
import subprocess
from typing import Sequence, Optional

def run_script(path: Path | str, args: Optional[Sequence[str]] = None, *, check: bool = True, cwd: Optional[Path | str] = None):
    """Run an external script or binary safely using pathlib and subprocess.

    - `path` may be a Path or string. Prefer Path for cross-platform safety.
    - `args` is an optional sequence of additional CLI arguments.
    - Returns the CompletedProcess.
    """
    p = Path(path)
    cmd = [str(p)] + (list(args) if args else [])
    return subprocess.run(cmd, check=check, cwd=(str(cwd) if cwd is not None else None))
