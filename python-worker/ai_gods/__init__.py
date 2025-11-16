"""Compatibility shim exposing the repo's ai_gods package to python-worker tests."""
from pathlib import Path
import sys

_repo_root = Path(__file__).resolve().parents[1]
_project_root = _repo_root.parent
if str(_project_root) not in sys.path:
    sys.path.append(str(_project_root))

_upstream_pkg = _project_root / "ai_gods"
__path__ = [str(Path(__file__).parent)]
if _upstream_pkg.exists():
    __path__.append(str(_upstream_pkg))
