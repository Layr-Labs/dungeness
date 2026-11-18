"""Fixed-output MCP fixture. Never executes the supplied command."""
import json
import sys

for line in sys.stdin:
    request = json.loads(line)
    if "id" not in request:
        continue
    method = request.get("method")
    if method == "initialize":
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "openrsi", "version": "0.0.1"},
        }
    elif method == "tools/list":
        result = {"tools": [{
            "name": "research_exec",
            "description": "Return a fixed synthetic result; no command execution",
            "inputSchema": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        }]}
    elif method == "tools/call" and request.get("params", {}).get("name") == "research_exec":
        result = {"content": [{"type": "text", "text": "synthetic output 42"}]}
    else:
        print(json.dumps({
            "jsonrpc": "2.0", "id": request["id"],
            "error": {"code": -32601, "message": "Unsupported fixture method"},
        }), flush=True)
        continue
    print(json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": result}), flush=True)
