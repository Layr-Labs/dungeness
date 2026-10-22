from __future__ import annotations

import importlib.machinery
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from runtime_fixture import ROOT as FIXTURE_ROOT



def load_cli():
    path = FIXTURE_ROOT / "dungeness"
    loader = importlib.machinery.SourceFileLoader("dungeness_scaffold_cli", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class ScaffoldInitializationTests(unittest.TestCase):
    def test_run_spec_selects_scaffold_without_fresh_start(self) -> None:
        cli = load_cli()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "run.yaml"
            path.write_text((FIXTURE_ROOT / "run-specs/projects/dungeness/sample-starter.yaml")
                            .read_text().replace("mode: checkpoint", "mode: scaffold"))
            args = cli.run_arguments_for_spec(path, namespace="users/test", env_file=None, labels=[])
            with patch.dict(os.environ, {
                "DUNGENESS_NAMESPACE": "",
                "DUNGENESS_CONFIG": str(Path(temporary) / "missing-config.toml"),
            }):
                resolved = cli.resolve_run_spec_arguments(args)
            self.assertTrue(resolved.scaffold_start)
            self.assertFalse(resolved.fresh_start)
            self.assertEqual(resolved.run_spec_ref, "run-spec:users/test/sample-starter")
            _, run_spec = cli.load_run_spec(resolved.target)
            self.assertEqual(run_spec["web_search"], {"mode": "disabled"})


if __name__ == "__main__":
    unittest.main()
