"""Local Anthropic fixture launched in the gateway container."""
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import runpy
import ssl
import threading
import time


CANARY = "dungeness-verify-synthetic-provider-key"
PORT = 8443


class Provider(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_POST(self):
        if self.path != "/anthropic/v1/messages" or self.headers.get("x-api-key") != CANARY:
            self.send_error(403)
            return

        request = self.rfile.read(int(self.headers["Content-Length"]))
        payload = json.loads(request)
        with self.server.lock:
            self.server.requests += 1
            attempt = self.server.requests
            with self.server.events.open("a") as events:
                events.write(json.dumps({"request_sha256": hashlib.sha256(request).hexdigest()}) + "\n")

        if attempt == 1:
            body = {"type": "error", "error": {"type": "rate_limit_error", "message": "Fixture cooldown"}}
            status = 429
        elif attempt == 2:
            time.sleep(.25)
            body = {
                "id": "msg_fixture", "type": "message", "role": "assistant",
                "model": payload["model"], "content": [{"type": "text", "text": "42"}],
                "stop_reason": "end_turn", "stop_sequence": None,
                "usage": {"input_tokens": 2048, "output_tokens": 8},
            }
            status = 200
        else:
            self.send_error(400)
            return
        encoded = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        if status == 429:
            self.send_header("Retry-After", "0")
        self.end_headers()
        self.wfile.write(encoded)


if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", PORT), Provider) as server:
        server.events = Path(os.environ["TESTBED_USAGE_DIR"]) / "fixture-provider.jsonl"
        server.requests = 0
        server.lock = threading.Lock()
        tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        tls.load_cert_chain("/app/verify-cert.pem", "/app/verify-key.pem")
        server.socket = tls.wrap_socket(server.socket, server_side=True)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            runpy.run_path("/app/gateway.py", run_name="__main__")
        finally:
            server.shutdown()
            thread.join()
