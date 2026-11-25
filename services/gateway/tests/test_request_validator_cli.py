"""Exercise the documented offline checker with current and legacy schedules."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]


class RequestValidatorTests(unittest.TestCase):
    def check_request(self, provider, request, operation="responses", pricing=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text(json.dumps(request))
            command = [sys.executable, str(ROOT / "tools/validate-model-request.py"),
                       "--provider", provider, "--operation", operation, "--request", str(path)]
            if pricing:
                schedule = Path(directory) / "pricing.json"
                schedule.write_text(json.dumps(pricing))
                command += ["--pricing", str(schedule)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotIn("Traceback", result.stderr)
            return result.returncode, json.loads(result.stdout)

    def test_bundled_schedule_and_legacy_json(self):
        import yaml
        request = {"model": "gpt-6.2-sol", "input": "Reply OK", "max_output_tokens": 32}
        code, bundled = self.check_request("openai", request)
        self.assertEqual(code, 0, bundled)
        self.assertTrue(bundled["valid"])
        self.assertGreater(bundled["reservation_tokens"], 0)
        schedule = yaml.safe_load((ROOT / "services/gateway/pricing.yaml").read_text())
        code, legacy = self.check_request("openai", request, pricing=schedule)
        self.assertEqual(code, 0, legacy)
        self.assertEqual(bundled, legacy)

    def test_rejects_invalid_route_operation_shape_and_output(self):
        request = {"model": "gpt-6.2-sol", "input": "Reply OK", "max_output_tokens": 32}
        for provider, body, operation in [
            ("unknown", request, "responses"),
            ("openai-chatgpt", request, "chat/completions"),
            ("openai", [], "responses"),
            ("openai", {**request, "max_output_tokens": 65537}, "responses"),
        ]:
            with self.subTest(provider=provider, operation=operation, body=body):
                code, result = self.check_request(provider, body, operation)
                self.assertEqual(code, 1)
                self.assertFalse(result["valid"])


if __name__ == "__main__":
    unittest.main()
