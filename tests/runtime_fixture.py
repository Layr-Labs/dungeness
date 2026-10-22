"""Disposable runtime populated with synthetic records for compiler tests.

Production checkouts contain no task or benchmark. Copy current implementation
files so CLI path discovery and compiler compatibility remain exercised without
depending on another repository or leaving generated files in the source tree.
"""
import atexit
from pathlib import Path
import shutil
import tempfile

SOURCE = Path(__file__).resolve().parents[1]
_temporary = tempfile.TemporaryDirectory(prefix="dungeness-unit-runtime-")
atexit.register(_temporary.cleanup)
ROOT = Path(_temporary.name)

for name in ("src", "adapters", "agents", "services", "policies", "tools"):
    shutil.copytree(SOURCE / name, ROOT / name,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".env", ".env.*"))
for name in ("dungeness", ".env.example", "runtime-contract.json"):
    shutil.copy2(SOURCE / name, ROOT / name)
shutil.copytree(SOURCE / "tests/fixtures/runtime", ROOT, dirs_exist_ok=True)
