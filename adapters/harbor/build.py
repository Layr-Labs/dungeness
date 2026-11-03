#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Backward-compatible entry point for the Dungeness compiler.

The implementation moved to ``src/dungeness/compiler.py``. Executing it in
this module's namespace preserves the historical command path, import surface,
and module-level monkeypatch behavior used by downstream callers.
"""

from pathlib import Path


COMPILER_SOURCE = (
    Path(__file__).resolve().parents[2] / "src/dungeness/compiler.py"
)
exec(
    compile(COMPILER_SOURCE.read_bytes(), str(COMPILER_SOURCE), "exec"),
    globals(),
    globals(),
)
