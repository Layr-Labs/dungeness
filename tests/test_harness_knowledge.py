"""Knowledge is agent-owned; legacy service requests cannot be silently ignored."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_record_model import build, cli, write_run_spec


class HarnessKnowledgeTests(unittest.TestCase):
    def test_legacy_knowledge_requests_stop_before_checkout(self):
        for value in ({"ref": "knowledge-base:users/example/papers"}, {}, None):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "run.yaml"
                write_run_spec(path)
                document = build.load_yaml(path)
                document["initialization"]["knowledge_base"] = value
                path.write_text(build.yaml.safe_dump(document))
                with self.assertRaisesRegex(SystemExit, "bundle knowledge"):
                    cli.load_run_spec(str(path))
                with patch.object(build, "checkout") as checkout:
                    with self.assertRaisesRegex(ValueError, "bundle knowledge"):
                        build.build_task("sample-problem", "legacy-kb", namespace="users/test", run_spec=str(path))
                    checkout.assert_not_called()

    def test_current_specs_do_not_require_a_knowledge_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "run.yaml"
            write_run_spec(path)
            _, document = cli.load_run_spec(str(path))
            self.assertEqual(document["initialization"], {"mode": "checkpoint"})
