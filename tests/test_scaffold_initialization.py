from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from adapters.harbor import build


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_cli():
    path = REPOSITORY_ROOT / "dungeness"
    loader = importlib.machinery.SourceFileLoader("dungeness_scaffold_cli", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class ScaffoldInitializationTests(unittest.TestCase):
    def test_scaffold_is_neutral_and_outside_candidate(self) -> None:
        scaffold = build.resolve_scaffold(
            "scaffolds/ecdsa-point-add-sdk-v1/scaffold.yaml"
        )
        self.assertEqual(
            scaffold["candidate_path"].as_posix(), "src/point_add"
        )
        self.assertEqual(scaffold["shots"], [1, 64, 512, 9024])
        for destination in scaffold["trusted_files"]:
            self.assertFalse(
                destination.is_relative_to(scaffold["candidate_path"])
            )
        stub = scaffold["candidate_stub"].read_text(encoding="utf-8")
        self.assertIn("pub fn build() -> Vec<Op>", stub)
        self.assertNotIn("kaliski", stub.lower())
        self.assertNotIn("modular", stub.lower())

    def test_progressive_patch_uses_final_authoritative_stage(self) -> None:
        source = r'''
fn main() {
    println!("\n-- correctness tests ({} shots) --", NUM_TESTS);
    let xof = fiat_shamir_seed(&ops);
    let r = run_tests(&ops, &regs, total_qubits, num_bits, xof, NUM_TESTS);
    println!("  tested shots            : {}", r.n_shots);
    println!("  classical mismatches    : {}", r.classical_failures);
    println!("  phase-garbage batches   : {}", r.phase_garbage_batches);
    println!("  ancilla-garbage batches : {}", r.ancilla_garbage_batches);
    if !r.ok {
        let reason = r.fail_reason.clone().unwrap_or_else(|| "(no detail)".into());
        println!("\n!! correctness FAILED: {reason}");
        std::process::exit(1);
    }
    println!("  all {} shots OK", r.n_shots);
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "eval_circuit.rs"
            path.write_text(source, encoding="utf-8")
            build.patch_progressive_eval(path, [1, 64, 512, 9024])
            patched = path.read_text(encoding="utf-8")
        self.assertIn("&[1, 64, 512, NUM_TESTS]", patched)
        self.assertIn("correctness FAILED at {} shots", patched)
        self.assertIn("final_report.expect", patched)

    def test_run_spec_selects_scaffold_without_fresh_start(self) -> None:
        cli = load_cli()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "run.yaml"
            path.write_text((REPOSITORY_ROOT / "run-specs/projects/dungeness/ecdsa-starter.yaml")
                            .read_text().replace("mode: checkpoint", "mode: scaffold"))
            args = cli.run_arguments_for_spec(path, namespace="users/test", env_file=None, labels=[])
            with patch.dict(os.environ, {
                "DUNGENESS_NAMESPACE": "",
                "DUNGENESS_CONFIG": str(Path(temporary) / "missing-config.toml"),
            }):
                resolved = cli.resolve_run_spec_arguments(args)
            self.assertTrue(resolved.scaffold_start)
            self.assertFalse(resolved.fresh_start)
            self.assertEqual(resolved.run_spec_ref, "run-spec:users/test/ecdsa-starter")
            _, run_spec = cli.load_run_spec(resolved.target)
            self.assertEqual(run_spec["web_search"], {"mode": "disabled"})


if __name__ == "__main__":
    unittest.main()
