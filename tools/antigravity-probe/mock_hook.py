"""Observe documented invocation hooks in a synthetic, offline session."""
import json
from pathlib import Path
import sys

payload = json.loads(sys.stdin.read(1024 * 1024))
record = {
    "phase": sys.argv[1],
    "model": payload.get("modelName"),
    "invocation": payload.get("invocationNum"),
    "fields": sorted(payload),
}
with Path(sys.argv[2]).open("a") as handle:
    handle.write(json.dumps(record) + "\n")
print("{}")
