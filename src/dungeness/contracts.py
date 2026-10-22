"""Public runtime capabilities, independent of execution and service imports."""
from __future__ import annotations

import json
from pathlib import Path


def runtime_contract(root: Path) -> dict:
    """Read the capability declaration shipped with a runtime checkout."""
    document = json.loads((root / "runtime-contract.json").read_text())
    if (not isinstance(document, dict)
            or type(document.get("schema_version")) is not int
            or document["schema_version"] != 1
            or document.get("runtime") != "dungeness"):
        raise ValueError("Unsupported Dungeness runtime contract")
    capabilities = document.get("capabilities")
    if (not isinstance(capabilities, list)
            or any(not isinstance(item, str) or not item for item in capabilities)
            or len(set(capabilities)) != len(capabilities)):
        raise ValueError("Invalid Dungeness runtime capabilities")
    return document
