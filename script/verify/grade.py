"""Grade the transferred candidate in Harbor's offline verifier."""
import json
from pathlib import Path
import socket


assert set(socket.if_nameindex()) == {(1, "lo")}, "Verifier has a network interface"
expected = Path("/tests/evaluator/check.txt").read_text().strip()
candidate = Path("/workspace/repo/solution/value.txt").read_text().strip()
Path("/logs/verifier/reward.json").write_text(
    json.dumps({"sample_score": int(expected) if candidate == expected else 0})
)
