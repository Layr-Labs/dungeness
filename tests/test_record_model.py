from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import hashlib
import importlib.machinery
import importlib.util
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


cli = load_module("dungeness_cli", REPOSITORY_ROOT / "dungeness")
build = load_module(
    "dungeness_harbor_build",
    REPOSITORY_ROOT / "adapters/harbor/build.py",
)
compiler = load_module(
    "dungeness_compiler",
    REPOSITORY_ROOT / "src/dungeness/compiler.py",
)
candidate_state = load_module(
    "dungeness_candidate_state",
    REPOSITORY_ROOT / "agents/common/candidate_state.py",
)


MODEL = {"provider": "openai", "upstream_id": "openai/gpt-6-astra",
         "request_model": "gpt-6-astra", "api": "openai-responses", "name_format": "request"}


def fixture_agent(module=build):
    return {**module.load_agent("command"), "model": MODEL, "model_access": {"models": [MODEL]}}


def write_run_spec(path: Path, *, namespace: str = "users/bx") -> None:
    path.write_text(
        "\n".join(
            (
                "schema_version: 1",
                "type: run-spec",
                f"namespace: {namespace}",
                "id: ecdsa-fail-command-1usd",
                "task: task:projects/dungeness/ecdsa-starter",
                "agent: agent:projects/dungeness/command",
                "model_access:",
                "  models:",
                "    - provider: openai",
                "      upstream_id: openai/gpt-6-astra",
                "      request_model: gpt-6-astra",
                "      api: openai-responses",
                "      name_format: request",
                "checkpoint: checkpoint:public/github/layr-labs/"
                "ecdsafail-challenge/"
                "62ae3d00d1e01d7bc640b5163cfea8dabffd8392",
                "budget:",
                "  max_usd: 1",
                "initialization:",
                "  mode: checkpoint",
                "labels:",
                "  purpose: baseline",
                "runtime:",
                "  env_file: .env",
                "  keep_render: false",
                "  keep_images: false",
                "  agent_timeout_sec: 2700",
            )
        )
        + "\n",
        encoding="utf-8",
    )


class CompilerCompatibilityTests(unittest.TestCase):
    def test_cli_uses_primary_compiler_entrypoint(self) -> None:
        self.assertEqual(
            cli.BUILD_SCRIPT,
            REPOSITORY_ROOT / "src/dungeness/compiler.py",
        )

    def test_legacy_harbor_module_preserves_compiler_surface(self) -> None:
        self.assertEqual(
            Path(build.resolve_scaffold.__code__.co_filename),
            REPOSITORY_ROOT / "src/dungeness/compiler.py",
        )
        agent = fixture_agent(build)
        task = REPOSITORY_ROOT / "tasks/projects/dungeness/ecdsa-starter"
        self.assertEqual(
            build.build_harbor_job("compatibility-test", agent, task),
            compiler.build_harbor_job(
                "compatibility-test",
                fixture_agent(compiler),
                task,
            ),
        )

    def test_legacy_module_level_overrides_still_apply(self) -> None:
        original = build.RUNS_ROOT
        try:
            build.RUNS_ROOT = Path("/tmp/dungeness-compatibility-runs")
            self.assertEqual(
                build.run_directory("users/bx", "example"),
                Path("/tmp/dungeness-compatibility-runs/users/bx/example"),
            )
        finally:
            build.RUNS_ROOT = original

    def test_legacy_and_primary_commands_have_identical_help(self) -> None:
        outputs = []
        for path in (
            REPOSITORY_ROOT / "adapters/harbor/build.py",
            REPOSITORY_ROOT / "src/dungeness/compiler.py",
        ):
            result = subprocess.run(
                [sys.executable, str(path), "--help"],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            outputs.append((result.stdout, result.stderr))
        self.assertEqual(outputs[0], outputs[1])

    def test_legacy_and_primary_commands_print_identical_build_output(self) -> None:
        outputs = []
        arguments = [
            "build.py",
            "ecdsa-fail",
            "--namespace",
            "users/bx",
            "--checkpoint",
            "62ae3d0",
        ]
        for module in (build, compiler):
            stream = io.StringIO()
            with (
                patch.object(
                    module,
                    "build_task",
                    return_value=Path("/tmp/dungeness-rendered-task"),
                ),
                patch.object(sys, "argv", arguments),
                redirect_stdout(stream),
            ):
                module.main()
            outputs.append(stream.getvalue())
        self.assertEqual(outputs, ["/tmp/dungeness-rendered-task\n"] * 2)


class RecordModelTests(unittest.TestCase):
    def test_disabled_web_search_zeros_the_effective_web_budget(self) -> None:
        authored = {
            "web": {"searches": 100, "fetches": 200},
            "model": {"requests": 500, "total_tokens": 1_000_000},
        }
        effective = build.apply_web_search_mode_to_budget(
            authored,
            "disabled",
        )
        self.assertEqual(
            effective["web"],
            {"searches": 0, "fetches": 0},
        )
        self.assertEqual(
            authored["web"],
            {"searches": 100, "fetches": 200},
        )
        self.assertIs(
            build.apply_web_search_mode_to_budget(authored, "optional"),
            authored,
        )

    def test_compose_requires_exa_key_only_with_a_nonzero_web_budget(self) -> None:
        web = {
            "historical_cutoff": {
                "end_published_date": "2026-05-28T23:59:59.999Z",
            },
            "search": {"max_results": 25},
        }
        model_budget = {"requests": 1, "total_tokens": 1000}
        no_web = build.yaml.safe_load(
            build.build_compose(
                "no-web-test",
                web,
                {
                    "web": {"searches": 0, "fetches": 0},
                    "model": model_budget,
                },
            )
        )
        no_web_environment = no_web["services"]["gateway"]["environment"]
        self.assertNotIn("EXA_API_KEY", no_web_environment)
        self.assertEqual(no_web_environment["MAX_SEARCHES"], "0")
        self.assertEqual(no_web_environment["MAX_FETCHES"], "0")

        with_web = build.yaml.safe_load(
            build.build_compose(
                "with-web-test",
                web,
                {
                    "web": {"searches": 1, "fetches": 1},
                    "model": model_budget,
                },
            )
        )
        self.assertEqual(
            with_web["services"]["gateway"]["environment"]["EXA_API_KEY"],
            "${EXA_API_KEY:?EXA_API_KEY is required}",
        )


    def test_candidate_state_round_trips_directory_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate"
            snapshot = root / "snapshot"
            candidate.mkdir()
            (candidate / "mod.rs").write_text("baseline", encoding="utf-8")
            candidate_state.replace_path(candidate, snapshot)
            baseline_digest = candidate_state.digest_path(snapshot)
            (candidate / "mod.rs").write_text("regression", encoding="utf-8")
            candidate_state.replace_path(snapshot, candidate)
            self.assertEqual(
                (candidate / "mod.rs").read_text(encoding="utf-8"),
                "baseline",
            )
            self.assertEqual(candidate_state.digest_path(candidate), baseline_digest)


    def test_namespace_resolution_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.toml"
            cli.write_user_config(config_path, "users/configured")

            self.assertEqual(
                cli.resolve_namespace(
                    "users/explicit",
                    environment={"DUNGENESS_NAMESPACE": "users/environment"},
                    config_path=config_path,
                ),
                "users/explicit",
            )
            self.assertEqual(
                cli.resolve_namespace(
                    None,
                    environment={"DUNGENESS_NAMESPACE": "users/environment"},
                    config_path=config_path,
                ),
                "users/environment",
            )
            self.assertEqual(
                cli.resolve_namespace(
                    None,
                    environment={},
                    config_path=config_path,
                ),
                "users/configured",
            )

    def test_init_writes_user_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.toml"
            environment = {
                **os.environ,
                "DUNGENESS_CONFIG": str(config_path),
            }
            args = cli.argparse.Namespace(
                namespace="users/bx",
                force=False,
            )
            previous_root = cli.REPO_ROOT
            cli.REPO_ROOT = Path(directory) / "repository"
            try:
                with patch.dict(os.environ, environment, clear=True):
                    self.assertEqual(cli.initialize(args), 0)
            finally:
                cli.REPO_ROOT = previous_root
            self.assertEqual(
                cli.load_user_config(config_path)["namespace"],
                "users/bx",
            )
            for collection in ("agents", "tasks", "experiments", "run-specs", "runs"):
                self.assertTrue(
                    (Path(directory) / "repository" / collection / "users/bx").is_dir()
                )

    def test_setup_creates_env_from_template(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env.example").write_text("EXA_API_KEY=\n", encoding="utf-8")
            previous_root = cli.REPO_ROOT
            cli.REPO_ROOT = root
            try:
                with (
                    patch.object(cli.shutil, "which", return_value="/usr/bin/tool"),
                    patch.object(
                        cli.subprocess,
                        "run",
                        return_value=cli.subprocess.CompletedProcess(
                            ["docker", "info"],
                            0,
                        ),
                    ),
                ):
                    self.assertEqual(
                        cli.setup_environment(cli.argparse.Namespace()),
                        0,
                    )
            finally:
                cli.REPO_ROOT = previous_root
            self.assertEqual(
                (root / ".env").read_text(encoding="utf-8"),
                "EXA_API_KEY=\n",
            )

    def test_run_spec_null_tokens_disable_the_inherited_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spec.yaml"
            write_run_spec(path)
            _, spec = cli.load_run_spec(str(path))
            spec["budget"]["max_model_tokens"] = None
            cli.write_yaml(path, spec)
            args = cli.run_arguments_for_spec(path, namespace=None, env_file=None, labels=[])
            resolved = cli.resolve_run_spec_arguments(args)
            self.assertTrue(resolved.no_model_token_limit)
            self.assertIsNone(resolved.max_model_tokens)
            args = cli.run_arguments_for_spec(path, namespace=None, env_file=None, labels=[])
            args.max_model_tokens = 100
            resolved = cli.resolve_run_spec_arguments(args)
            self.assertFalse(getattr(resolved, "no_model_token_limit", False))
            self.assertEqual(resolved.max_model_tokens, 100)

    def test_run_spec_yaml_resolves_with_cli_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_spec_path = Path(directory) / "run-spec.yaml"
            write_run_spec(run_spec_path)
            args = cli.argparse.Namespace(
                target=str(run_spec_path),
                agent=None,
                checkpoint=None,
                fresh_start=None,
                run_id=None,
                namespace=None,
                label=["owner=bx"],
                resume_from=None,
                max_model_tokens=None,
                max_usd=2.0,
                env_file=None,
                keep_render=None,
            )
            resolved = cli.resolve_run_spec_arguments(args)
            self.assertEqual(resolved.task, "ecdsa-starter")
            self.assertEqual(resolved.agent, "command")
            self.assertIsNone(resolved.namespace)
            self.assertEqual(
                resolved.run_spec_ref,
                "run-spec:users/bx/ecdsa-fail-command-1usd",
            )
            self.assertTrue(
                resolved.checkpoint.endswith(
                    "62ae3d00d1e01d7bc640b5163cfea8dabffd8392"
                )
            )
            self.assertEqual(resolved.max_usd, 2.0)
            self.assertEqual(resolved.agent_timeout_sec, 2700)
            self.assertEqual(
                resolved.label,
                ["purpose=baseline", "owner=bx"],
            )
            self.assertFalse(resolved.fresh_start)
            self.assertEqual(resolved.env_file, ".env")
            self.assertFalse(resolved.keep_render)
            self.assertFalse(resolved.keep_images)
            self.assertEqual(
                resolved.run_spec_path,
                run_spec_path.resolve(),
            )

            resolved.namespace = "users/bx"
            command = cli.build_command(resolved, "test-run")
            self.assertIn("--run-spec", command)
            self.assertIn(str(resolved.run_spec_path), command)
            self.assertIn("--run-spec-namespace", command)
            self.assertIn("users/bx", command)
            self.assertIn("--agent-timeout-sec", command)
            self.assertIn("2700", command)

    def test_run_spec_can_keep_images_and_cli_can_override_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_spec_path = Path(directory) / "run-spec.yaml"
            write_run_spec(run_spec_path)
            run_spec_path.write_text(
                run_spec_path.read_text(encoding="utf-8").replace(
                    "  keep_images: false\n",
                    "  keep_images: true\n",
                ),
                encoding="utf-8",
            )

            configured = cli.resolve_run_spec_arguments(
                cli.run_arguments_for_spec(
                    run_spec_path,
                    namespace=None,
                    env_file=None,
                    labels=[],
                )
            )
            self.assertTrue(configured.keep_images)

            override = cli.run_arguments_for_spec(
                run_spec_path,
                namespace=None,
                env_file=None,
                labels=[],
            )
            override.keep_images = False
            resolved_override = cli.resolve_run_spec_arguments(override)
            self.assertFalse(resolved_override.keep_images)

    def test_run_spec_namespace_defaults_from_user_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_spec_path = Path(directory) / "run-spec.yaml"
            write_run_spec(run_spec_path)
            run_spec_path.write_text(
                run_spec_path.read_text(encoding="utf-8").replace(
                    "namespace: users/bx\n",
                    "",
                ),
                encoding="utf-8",
            )
            args = cli.argparse.Namespace(
                target=str(run_spec_path),
                agent=None,
                checkpoint=None,
                fresh_start=None,
                run_id=None,
                namespace=None,
                label=[],
                resume_from=None,
                max_model_tokens=None,
                max_usd=None,
                env_file=None,
                keep_render=None,
            )
            with patch.object(
                cli,
                "resolve_namespace",
                return_value="users/alice",
            ):
                resolved = cli.resolve_run_spec_arguments(args)
            self.assertEqual(
                resolved.run_spec_ref,
                "run-spec:users/alice/ecdsa-fail-command-1usd",
            )

    def test_default_run_id_uses_run_spec_identity(self) -> None:
        args = cli.argparse.Namespace(
            run_spec_ref=(
                "run-spec:users/bx/"
                "ecdsa-effort-sweep-codex-subscription-c6f6d2c-low"
            ),
            task="ecdsa-fail",
            checkpoint="c6f6d2c7f50353259241e296458afb0e651e6c37",
            agent="codex-subscription",
        )
        run_id = cli.default_run_id(args)
        self.assertRegex(
            run_id,
            (
                r"^ecdsa-effort-sweep-codex-subscription-c6f6d2c-low-"
                r"\d{8}T\d{6}Z-[0-9a-f]{8}$"
            ),
        )
        self.assertLessEqual(len(run_id), 128)

    def test_transcript_server_command_targets_exact_run(self) -> None:
        run_dir = (
            REPOSITORY_ROOT
            / "runs/users/bx/example-run"
        )
        self.assertEqual(
            cli.transcript_server_command(run_dir),
            (
                "python3 tools/transcripts/serve_gateway_transcripts.py "
                "runs/users/bx/example-run"
            ),
        )

    def test_long_run_spec_identity_is_compacted_but_remains_recognizable(self) -> None:
        local_id = "experiment-" + ("long-section-" * 10) + "xhigh"
        args = cli.argparse.Namespace(
            run_spec_ref=f"run-spec:users/bx/{local_id}",
            task="ecdsa-fail",
            checkpoint="c6f6d2c7f50353259241e296458afb0e651e6c37",
            agent="codex-subscription",
        )
        run_id = cli.default_run_id(args)
        self.assertLessEqual(len(run_id), 128)
        self.assertTrue(run_id.startswith("experiment-"))
        self.assertIn("xhigh-", run_id)
        self.assertRegex(run_id, r"-[0-9a-f]{8}-.*-\d{8}T\d{6}Z-[0-9a-f]{8}$")

    def test_run_spec_path_defaults_from_user_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_spec_path = root / "run-specs/users/alice/sample.yaml"
            run_spec_path.parent.mkdir(parents=True)
            write_run_spec(run_spec_path, namespace="users/alice")

            previous_root = cli.REPO_ROOT
            cli.REPO_ROOT = root
            try:
                with patch.object(
                    cli,
                    "resolve_namespace",
                    return_value="users/alice",
                ):
                    resolved_path, _ = cli.load_run_spec("sample.yaml")
            finally:
                cli.REPO_ROOT = previous_root
            self.assertEqual(resolved_path, run_spec_path.resolve())

    def test_agent_and_task_short_names_prefer_default_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for record_type, filename in (
                ("agent", "agent.yaml"),
                ("task", "task.yaml"),
            ):
                collection = f"{record_type}s"
                for namespace in ("users/bx", "projects/dungeness"):
                    path = (
                        root
                        / collection
                        / namespace
                        / "custom"
                        / filename
                    )
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(
                        "\n".join(
                            (
                                "schema_version: 1",
                                f"type: {record_type}",
                                f"namespace: {namespace}",
                                "id: custom",
                            )
                        )
                        + "\n",
                        encoding="utf-8",
                    )

            previous_root = cli.REPO_ROOT
            cli.REPO_ROOT = root
            try:
                with patch.object(
                    cli,
                    "resolve_namespace",
                    return_value="users/bx",
                ):
                    self.assertEqual(
                        cli.resolve_installed_record("custom", "agent"),
                        ("users/bx", "custom"),
                    )
                    self.assertEqual(
                        cli.resolve_installed_record("custom", "task"),
                        ("users/bx", "custom"),
                    )
                self.assertEqual(
                    cli.resolve_installed_record(
                        "agent:projects/dungeness/custom",
                        "agent",
                    ),
                    ("projects/dungeness", "custom"),
                )
            finally:
                cli.REPO_ROOT = previous_root

    def test_run_spec_rejects_wrong_agent_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "run-spec.yaml"
            config.write_text(
                "\n".join(
                    (
                        "schema_version: 1",
                        "type: run-spec",
                        "namespace: users/bx",
                        "id: wrong-agent-scope",
                        "task: task:projects/dungeness/ecdsa-starter",
                        "agent: agent:users/bx/command",
                        "checkpoint: checkpoint:public/github/layr-labs/"
                        "ecdsafail-challenge/"
                        "62ae3d00d1e01d7bc640b5163cfea8dabffd8392",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            args = cli.argparse.Namespace(
                target=str(config),
                agent=None,
                checkpoint=None,
                fresh_start=None,
                run_id=None,
                namespace=None,
                label=[],
                resume_from=None,
                max_model_tokens=None,
                max_usd=None,
                env_file=None,
                keep_render=None,
            )
            with self.assertRaisesRegex(SystemExit, "does not match"):
                cli.resolve_run_spec_arguments(args)

    def test_checkpoint_resolves_unique_commit_prefix(self) -> None:
        checkpoint = build.resolve_checkpoint(
            "62ae3d0",
        )
        self.assertEqual(
            checkpoint["namespace"],
            "public/github/layr-labs/ecdsafail-challenge",
        )
        self.assertEqual(
            checkpoint["id"],
            "62ae3d00d1e01d7bc640b5163cfea8dabffd8392",
        )
        self.assertEqual(
            checkpoint["ref"],
            "checkpoint:public/github/layr-labs/ecdsafail-challenge/"
            "62ae3d00d1e01d7bc640b5163cfea8dabffd8392",
        )
        self.assertEqual(
            checkpoint["path"].relative_to(REPOSITORY_ROOT).parent.as_posix(),
            "checkpoints/ecdsafail-challenge",
        )

    def test_problem_is_semantic_and_publicly_scoped(self) -> None:
        problem = build.resolve_problem(
            "problem:public/ecdsafail-challenge/ecdsa-fail"
        )
        self.assertEqual(problem["id"], "ecdsa-fail")
        self.assertEqual(problem["namespace"], "public/ecdsafail-challenge")
        self.assertEqual(
            problem["ref"],
            "problem:public/ecdsafail-challenge/ecdsa-fail",
        )
        self.assertEqual(
            problem["data"]["metric"]["name"],
            "ecdsafail_score",
        )

    def test_task_binds_problem_checkpoint_interface_and_verifier(self) -> None:
        task = build.load_yaml(
            REPOSITORY_ROOT / "tasks/projects/dungeness/ecdsa-starter/task.yaml"
        )
        problem = build.resolve_problem(task["relations"]["problem"])
        checkpoint = build.resolve_checkpoint("62ae3d0")
        interface = task["interfaces"][checkpoint["interface"]]
        verifier = REPOSITORY_ROOT / "verifiers" / interface["verifier"]

        self.assertEqual(
            problem["ref"],
            "problem:public/ecdsafail-challenge/ecdsa-fail",
        )
        self.assertEqual(
            interface["candidate"]["allowed_paths"],
            ["src/point_add"],
        )
        self.assertTrue((verifier / "evaluator.lock.yaml").is_file())

    def test_system_components_use_reserved_namespace(self) -> None:
        manifests = (
            ("policies/network/mediated.yaml", "policy", "gateway-only"),
            ("policies/web/exa.yaml", "policy", "exa-shared"),
            ("policies/budget/default.yaml", "policy", "default"),
            ("services/gateway/service.yaml", "service", "gateway"),
            ("services/gateway/pricing.yaml", "policy", "model-pricing"),
            ("adapters/harbor/adapter.yaml", "adapter", "harbor"),
        )
        for relative_path, record_type, local_id in manifests:
            path = REPOSITORY_ROOT / relative_path
            manifest = build.load_yaml(path)
            build.validate_manifest_identity(manifest, record_type, path)
            self.assertEqual(manifest["namespace"], "system/dungeness")
            self.assertEqual(manifest["id"], local_id)










    def test_experiment_create_materializes_factorial_run_specs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task_path = root / "tasks/demo/task.yaml"
            task_path.parent.mkdir(parents=True)
            task_path.write_text(
                "\n".join(
                    (
                        "schema_version: 1",
                        "type: task",
                        "namespace: users/bx",
                        "id: demo",
                        "relations:",
                        "  problem: problem:public/demo/objective",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            for agent_id in ("alpha", "beta"):
                agent_path = root / f"agents/{agent_id}/agent.yaml"
                agent_path.parent.mkdir(parents=True)
                agent_path.write_text(
                    "\n".join(
                        (
                            "schema_version: 1",
                            "type: agent",
                            "namespace: projects/dungeness",
                            f"id: {agent_id}",
                        )
                    )
                    + "\n",
                    encoding="utf-8",
                )
            checkpoint_ids = ("a" * 40, "b" * 40)
            for checkpoint_id in checkpoint_ids:
                checkpoint_path = root / f"checkpoints/demo/{checkpoint_id}.yaml"
                checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
                checkpoint_path.write_text(
                    "\n".join(
                        (
                            "schema_version: 1",
                            "type: checkpoint",
                            "namespace: public/github/example/demo",
                            f"id: {checkpoint_id}",
                        )
                    )
                    + "\n",
                    encoding="utf-8",
                )
            experiment_path = (
                root
                / "experiments/users/bx/runtime-sweep/experiment.yaml"
            )
            experiment_path.parent.mkdir(parents=True)
            experiment_path.write_text(
                "\n".join(
                    (
                        "schema_version: 1",
                        "type: experiment",
                        "id: runtime-sweep",
                        "labels:",
                        "  purpose: runtime-comparison",
                        "relations:",
                        "  task: task:users/bx/demo",
                        "design:",
                        "  kind: full-factorial",
                        "  repetitions: 2",
                        "  controls:",
                        "    model_access:",
                        "      models:",
                        "        - provider: openai",
                        "          upstream_id: openai/gpt-6-astra",
                        "          request_model: gpt-6-astra",
                        "          api: openai-responses",
                        "          name_format: request",
                        "    task: task:users/bx/demo",
                        "    budget:",
                        "      max_usd: 1",
                        "      max_model_tokens: 1000",
                        "    initialization:",
                        "      mode: checkpoint",
                        "  axes:",
                        "    agents:",
                        "      - ref: agent:projects/dungeness/alpha",
                        "      - ref: agent:projects/dungeness/beta",
                        "    checkpoints:",
                        f"      - ref: checkpoint:public/github/example/demo/{checkpoint_ids[0]}",
                        f"      - ref: checkpoint:public/github/example/demo/{checkpoint_ids[1]}",
                        "run_labels:",
                        "  purpose: runtime-comparison",
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            previous_root = cli.REPO_ROOT
            cli.REPO_ROOT = root
            try:
                with patch.object(
                    cli,
                    "resolve_namespace",
                    return_value="users/bx",
                ):
                    result = cli.create_experiment(
                        cli.argparse.Namespace(
                            target="runtime-sweep",
                        )
                    )
            finally:
                cli.REPO_ROOT = previous_root

            self.assertEqual(result, 0)
            experiment = build.load_yaml(experiment_path)
            self.assertEqual(experiment["namespace"], "users/bx")
            self.assertEqual(experiment["design"]["planned_runs"], 8)
            self.assertEqual(experiment["design"]["nominal_budget_usd"], 8.0)
            self.assertEqual(
                experiment["relations"]["problem"],
                "problem:public/demo/objective",
            )
            self.assertEqual(len(experiment["relations"]["run_specs"]), 8)
            run_specs = list(
                (root / "run-specs/users/bx/runtime-sweep").glob("*.yaml")
            )
            self.assertEqual(len(run_specs), 8)
            for path in run_specs:
                run_spec = build.load_yaml(path)
                self.assertEqual(run_spec["budget"]["max_usd"], 1.0)
                self.assertEqual(run_spec["labels"]["experiment"], "runtime-sweep")
                self.assertIn(run_spec["labels"]["repetition"], {"1", "2"})
                self.assertFalse(run_spec["runtime"]["keep_images"])

            args = dict(target=str(experiment_path), namespace="users/bx", env_file=None,
                        label=[], yes=True, continue_on_error=False)
            with patch.object(cli, "REPO_ROOT", root), patch.object(cli, "execute_run") as execute:
                self.assertEqual(cli.run_experiment(argparse.Namespace(**args, dry_run=True)), 0)
                execute.assert_not_called()
                execute.return_value = 0
                self.assertEqual(cli.run_experiment(argparse.Namespace(**args, dry_run=False)), 0)
                self.assertEqual(execute.call_count, 8)
                self.assertEqual([Path(call.args[0].target).resolve() for call in execute.call_args_list],
                    [cli.load_qualified_record(ref, "run-spec")[0].resolve()
                     for ref in experiment["relations"]["run_specs"]])


    def test_native_reasoning_options_require_harness_migration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.yaml"
            write_run_spec(path)
            with path.open("a") as output:
                output.write("agent_options:\n  reasoning_effort: low\n  reasoning_summary: detailed\n")
            with self.assertRaisesRegex(SystemExit, "Native agent_options are retired"):
                cli.resolve_run_spec_arguments(cli.run_arguments_for_spec(
                    path, namespace=None, env_file=None, labels=[]))

    def test_checkpoint_samples_are_commit_addressed(self) -> None:
        expected_positions = {
            "c6f6d2c": 0,
            "62ae3d0": 868,
            "4b9cfbb": 966,
            "afcc72e": 1326,
        }
        for prefix, position in expected_positions.items():
            checkpoint = build.resolve_checkpoint(
                prefix,
            )
            self.assertTrue(checkpoint["id"].startswith(prefix))
            self.assertEqual(checkpoint["commit"], checkpoint["id"])
            self.assertEqual(
                checkpoint["history"]["distance_from_anchor"], position
            )
            self.assertEqual(
                checkpoint["history"]["counting_method"],
                "git-rev-list-ancestry-path-count",
            )
            manifest = build.load_yaml(checkpoint["path"])
            self.assertEqual(manifest["id"], checkpoint["id"])
            self.assertNotIn("name", manifest)
            self.assertNotIn("relations", manifest)
            self.assertIn(
                checkpoint["interface"],
                {"point-add-file-v1", "point-add-module-v1"},
            )
            self.assertNotIn("verifier", manifest["data"])
        with self.assertRaisesRegex(ValueError, "commit prefix"):
            build.resolve_checkpoint("k1")

    def test_harbor_metadata_uses_checkpoint_identity(self) -> None:
        checkpoint_id = (
            "checkpoint:public/github/layr-labs/ecdsafail-challenge/"
            "62ae3d00d1e01d7bc640b5163cfea8dabffd8392"
        )
        task = build.build_task_toml(
            "ecdsa-fail",
            "users/bx",
            "62ae3d00d1e01d7bc640b5163cfea8dabffd8392",
            "62ae3d00d1e01d7bc640b5163cfea8dabffd8392",
            [PurePosixPath("src/point_add")],
            "command",
            "test",
            ["test"],
            {
                "timeout_sec": 1,
                "build_timeout_sec": 1,
                "cpus": 1,
                "memory_mb": 1,
                "storage_mb": 1,
            },
            {
                "timeout_sec": 1,
                "build_timeout_sec": 1,
                "cpus": 1,
                "memory_mb": 1,
                "storage_mb": 1,
            },
            checkpoint_meta={
                "id": checkpoint_id,
                "initialization": "blank",
            },
        )
        metadata = tomllib.loads(task)["metadata"]
        self.assertEqual(metadata["checkpoint"], checkpoint_id)
        self.assertEqual(metadata["initialization"], "blank")
        self.assertNotIn("trajectory", metadata)
        task_config = tomllib.loads(task)
        self.assertEqual(
            task_config["verifier"]["environment"]["network_mode"],
            "public",
        )
        verifier_compose = build.yaml.safe_load(build.build_verifier_compose())
        self.assertEqual(
            verifier_compose["services"]["main"]["network_mode"],
            "none",
        )

    def test_harbor_job_accepts_temporary_task_path(self) -> None:
        agent = fixture_agent(build)
        self.assertIsNotNone(agent)
        self.assertEqual(agent["namespace"], "projects/dungeness")
        temporary_task = (
            Path(tempfile.gettempdir())
            / "dungeness-test-run-example"
            / "task"
        )
        job = build.yaml.safe_load(
            build.build_harbor_job("test-run", agent, temporary_task)
        )
        self.assertEqual(job["tasks"][0]["path"], str(temporary_task.resolve()))
        self.assertTrue(Path(job["jobs_dir"]).is_absolute())

    def test_resolved_run_record_uses_universal_envelope(self) -> None:
        agent = fixture_agent(build)
        self.assertIsNotNone(agent)
        checkpoint = build.resolve_checkpoint(
            "public/github/layr-labs/ecdsafail-challenge/62ae3d0",
        )
        record = build.build_run_record(
            run_id="test-run",
            run_namespace="users/bx",
            labels={"purpose": "test"},
            task_id="ecdsa-starter",
            task_namespace="projects/dungeness",
            task_path=REPOSITORY_ROOT / "tasks/projects/dungeness/ecdsa-starter/task.yaml",
            problem_spec=build.resolve_problem(
                "problem:public/ecdsafail-challenge/ecdsa-fail"
            ),
            checkpoint_spec=checkpoint,
            interface_id="point-add-module-v1",
            verifier_ref="ecdsa-fail/benchmark-sh",
            fresh_start=False,
            start_url=checkpoint["url"],
            start_commit=checkpoint["commit"],
            web_cutoff=checkpoint["web_cutoff"],
            candidate_paths=[PurePosixPath("src/point_add")],
            evaluator_url=checkpoint["url"],
            evaluator_commit=checkpoint["commit"],
            agent_id="command",
            agent_path=(
                REPOSITORY_ROOT
                / "agents/projects/dungeness/command/agent.yaml"
            ),
            agent=agent,
            agent_options={},
            metric_name="ecdsafail_score",
            direction="minimize",
            budget_policy={},
            max_usd=1.0,
            resume=None,
            configuration={
                "sources": {},
                "resolved": {"limits": {"max_usd": 1.0}},
                "generated": {
                    "task_toml": {"metadata": {"agent": "command"}},
                },
            },
        )
        self.assertEqual(record["type"], "run")
        self.assertEqual(record["id"], "test-run")
        self.assertEqual(record["namespace"], "users/bx")
        self.assertEqual(record["labels"], {"purpose": "test"})
        self.assertEqual(
            record["relations"]["task"],
            "task:projects/dungeness/ecdsa-starter",
        )
        self.assertEqual(
            record["relations"]["problem"],
            "problem:public/ecdsafail-challenge/ecdsa-fail",
        )
        self.assertEqual(
            record["relations"]["agent"],
            "agent:projects/dungeness/command",
        )
        self.assertEqual(
            record["relations"]["checkpoint"],
            "checkpoint:public/github/layr-labs/ecdsafail-challenge/"
            "62ae3d00d1e01d7bc640b5163cfea8dabffd8392",
        )
        self.assertEqual(
            record["data"]["checkpoint"]["web_cutoff"],
            "2026-05-28T23:59:59.999Z",
        )
        self.assertEqual(
            record["data"]["checkpoint"]["history"]["distance_from_anchor"],
            868,
        )
        self.assertEqual(
            record["data"]["task"]["interface"],
            "point-add-module-v1",
        )
        self.assertEqual(
            record["data"]["task"]["verifier"],
            "ecdsa-fail/benchmark-sh",
        )
        self.assertNotIn("verifier", record["data"]["checkpoint"])
        self.assertEqual(record["data"]["initialization"]["mode"], "checkpoint")
        self.assertEqual(
            record["data"]["configuration"]["generated"]["task_toml"]
            ["metadata"]["agent"],
            "command",
        )

    def test_configuration_source_snapshot_has_path_hash_and_document(self) -> None:
        path = (
            REPOSITORY_ROOT
            / "agents/projects/dungeness/command/agent.yaml"
        )
        document = build.load_yaml(path)
        snapshot = build.source_snapshot(path, document)
        self.assertEqual(
            snapshot["path"],
            "agents/projects/dungeness/command/agent.yaml",
        )
        self.assertEqual(len(snapshot["sha256"]), 64)
        self.assertEqual(snapshot["document"]["type"], "agent")

    def test_evaluator_patch_is_commit_scoped_and_snapshotted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checkout = root / "checkout"
            verifier = root / "verifier"
            checkout.mkdir()
            verifier.mkdir()
            subprocess.run(
                ["git", "-C", str(checkout), "init", "--quiet"],
                check=True,
            )
            target = checkout / "value.txt"
            target.write_text("before\n", encoding="utf-8")
            patch_path = verifier / "change.patch"
            patch_path.write_text(
                "--- a/value.txt\n"
                "+++ b/value.txt\n"
                "@@ -1 +1 @@\n"
                "-before\n"
                "+after\n",
                encoding="utf-8",
            )
            manifest = {
                "patches": [
                    {
                        "path": "change.patch",
                        "commits": ["a" * 40],
                    }
                ]
            }

            self.assertEqual(
                build.apply_evaluator_patches(
                    checkout,
                    verifier,
                    manifest,
                    "b" * 40,
                ),
                [],
            )
            self.assertEqual(target.read_text(encoding="utf-8"), "before\n")

            applied = build.apply_evaluator_patches(
                checkout,
                verifier,
                manifest,
                "a" * 40,
            )
            self.assertEqual(target.read_text(encoding="utf-8"), "after\n")
            self.assertEqual(applied[0]["commits"], ["a" * 40])
            self.assertEqual(
                applied[0]["file"]["path"],
                str(patch_path.resolve()),
            )
            self.assertEqual(len(applied[0]["file"]["sha256"]), 64)

    def test_retired_research_state_specs_fail_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.yaml"
            write_run_spec(path)
            path.write_text(path.read_text() + "research_state: {}\n")
            with self.assertRaisesRegex(SystemExit, "research_state has been removed"):
                cli.load_run_spec(str(path))
            with patch.object(build, "checkout") as checkout:
                with self.assertRaisesRegex(ValueError, "research_state has been removed"):
                    build.build_task(
                        "ecdsa-starter", "legacy-spec", namespace="users/bx",
                        run_spec=str(path),
                    )
                checkout.assert_not_called()

    def test_renderer_embeds_complete_configuration_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            previous_runs_root = build.RUNS_ROOT
            build.RUNS_ROOT = root / "runs"
            rendered_path = None
            run_spec_path = root / "run-spec.yaml"
            write_run_spec(run_spec_path)
            def fake_checkout(_url: str, _commit: str, destination: Path) -> None:
                destination.mkdir(parents=True)
                if destination.name == "start":
                    candidate = destination / "src/point_add"
                    candidate.mkdir(parents=True)
                    (candidate / "mod.rs").write_text("", encoding="utf-8")
                    return
                evaluator_lock = build.load_yaml(
                    REPOSITORY_ROOT
                    / "verifiers/ecdsa-fail/benchmark-sh/evaluator.lock.yaml"
                )
                for relative in evaluator_lock["include_paths"]:
                    path = destination / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("", encoding="utf-8")

            try:
                with (
                    patch.object(build, "checkout", side_effect=fake_checkout),
                    patch.object(
                        build,
                        "apply_evaluator_patches",
                        return_value=[
                            {
                                "commits": [
                                    "62ae3d00d1e01d7bc640b5163cfea8dabffd8392"
                                ],
                                "file": build.file_snapshot(
                                    REPOSITORY_ROOT
                                    / "verifiers/ecdsa-fail/benchmark-sh/"
                                    "low-memory-ops-streaming.patch"
                                ),
                            }
                        ],
                    ),
                    patch.object(
                        build,
                        "commit_timestamp",
                        return_value=datetime(
                            2026,
                            5,
                            29,
                            tzinfo=timezone.utc,
                        ),
                    ),
                ):
                    rendered_path = build.build_task(
                        "ecdsa-starter",
                        "configuration-test",
                        agent_id="command",
                        checkpoint="62ae3d0",
                        namespace="users/bx",
                        max_usd=1.0,
                        run_spec=str(run_spec_path),
                    )
                record = json.loads(
                    (rendered_path / "resolved-run.json").read_text(
                        encoding="utf-8"
                    )
                )
                configuration = record["data"]["configuration"]
                self.assertEqual(
                    configuration["sources"]["agent"]["document"]["type"],
                    "agent",
                )
                self.assertEqual(
                    configuration["sources"]["gateway"]["pricing"]["document"]["id"],
                    "model-pricing",
                )
                self.assertEqual(
                    configuration["resolved"]["model"]["pricing"]["provider"],
                    "openai",
                )
                self.assertEqual(
                    configuration["sources"]["run_spec"]["document"]["type"],
                    "run-spec",
                )
                self.assertEqual(
                    record["relations"]["run_spec"],
                    "run-spec:users/bx/ecdsa-fail-command-1usd",
                )
                self.assertEqual(
                    configuration["resolved"]["resources"]["agent"]["memory_mb"],
                    4096,
                )
                self.assertEqual(
                    configuration["resolved"]["resources"]["verifier"][
                        "memory_mb"
                    ],
                    8192,
                )
                self.assertEqual(
                    configuration["resolved"]["resources"]["agent"]["timeout_sec"],
                    2700,
                )
                self.assertEqual(
                    configuration["generated"]["task_toml"]["metadata"]["agent"],
                    "command",
                )
                self.assertEqual(
                    configuration["generated"]["docker_compose"]["services"]
                    ["gateway"]["environment"]["MAX_MODEL_USD"],
                    "1.0",
                )
                main_environment = (
                    configuration["generated"]["docker_compose"]["services"]
                    ["main"]["environment"]
                )
                self.assertNotIn("DUNGENESS_RESEARCH_MODEL", main_environment)
                self.assertEqual(
                    main_environment["DUNGENESS_AGENT_TIMEOUT_SEC"],
                    "2700",
                )
                self.assertEqual(
                    configuration["generated"]["docker_compose"]["services"]
                    ["dev-scorer"]["mem_limit"],
                    "8192m",
                )
                self.assertEqual(
                    len(
                        configuration["sources"]["verifier"][
                            "evaluator_patches"
                        ]
                    ),
                    1,
                )
                self.assertTrue(
                    (rendered_path / "environment/run_status.py").is_file()
                )
                self.assertTrue(
                    (rendered_path / "environment/candidate_state.py").is_file()
                )
                usage_volume = (
                    configuration["generated"]["docker_compose"]["services"]
                    ["gateway"]["volumes"][0]
                )
                self.assertTrue(usage_volume.startswith(str(root.resolve())))
                self.assertIn(
                    "/runs/users/bx/configuration-test/usage:",
                    usage_volume,
                )
                self.assertNotIn("knowledge_base", record["relations"])
                self.assertNotIn("knowledge_base", configuration["sources"])
                self.assertNotIn("knowledge-base", configuration["generated"]["docker_compose"]["services"])
                self.assertNotIn("DUNGENESS_KNOWLEDGE_BASE_URL", main_environment)
                self.assertFalse((rendered_path / "environment/knowledge_base.py").exists())
                self.assertNotIn("knowledge-base read", configuration["generated"]["instruction"])
                self.assertIn(
                    "## Workspace contract",
                    configuration["generated"]["instruction"],
                )
                self.assertIn(
                    "## Stable web-tool contract",
                    configuration["generated"]["instruction"],
                )
                self.assertNotIn(
                    "three consecutive valid",
                    configuration["generated"]["instruction"],
                )
                self.assertIn(
                    "untrusted external content",
                    configuration["generated"]["instruction"],
                )
                self.assertEqual(configuration["resolved"]["web_search"], {"mode": "optional"})
                self.assertNotIn("web_search_profile", configuration["sources"])
                self.assertNotIn("evaluation_profile", configuration["sources"])
                self.assertNotIn("prompt_profile", configuration["resolved"]["evaluation"])
                instruction = configuration["generated"]["instruction"]
                self.assertIn("## Evaluation interface", instruction)
                self.assertIn("the real benchmark", instruction)
                self.assertIn("hard wall-clock limit of 2700 seconds", instruction)
                self.assertIn("candidate-state save NAME", instruction)
                for retired in ("Evaluation loop", "Experimental web-research policy",
                                "Before changing the candidate", "Within the first",
                                "research-worker", "Stop starting new architectural"):
                    self.assertNotIn(retired, instruction)
                self.assertFalse((rendered_path / "environment/research_worker.py").exists())
                self.assertFalse(any(key.startswith("DUNGENESS_RESEARCH_") for key in
                    configuration["generated"]["docker_compose"]["services"]["main"]["environment"]))
                verifier_compose = build.load_yaml(
                    rendered_path / "tests/docker-compose.yaml"
                )
                self.assertEqual(
                    verifier_compose["services"]["main"]["network_mode"],
                    "none",
                )
            finally:
                build.RUNS_ROOT = previous_runs_root
                if rendered_path is not None and rendered_path.parent.exists():
                    shutil.rmtree(rendered_path.parent)

    def test_run_record_lifecycle_collects_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rendered = root / "temporary-render/test-run"
            rendered.mkdir(parents=True)
            resolved = {
                "schema_version": 1,
                "id": "test-run",
                "type": "run",
                "namespace": "users/bx",
                "created_at": None,
                "published_at": None,
                "labels": {"purpose": "test"},
                "relations": {},
                "data": {
                    "run_id": "test-run",
                    "status": "planned",
                    "configuration": {
                        "sources": {},
                        "resolved": {},
                        "generated": {},
                    },
                    "metric": {
                        "name": "ecdsafail_score",
                        "direction": "minimize",
                    },
                },
            }
            (rendered / "resolved-run.json").write_text(
                json.dumps(resolved),
                encoding="utf-8",
            )

            previous_root = cli.REPO_ROOT
            cli.REPO_ROOT = root
            try:
                with patch.object(
                    cli,
                    "repository_provenance",
                    return_value={
                        "vcs": "git",
                        "root": ".",
                        "available": True,
                        "commit": "a" * 40,
                        "branch": "experiment/test",
                        "capture_complete": True,
                        "dirty": False,
                        "reproducible_from_commit": True,
                        "status_sha256": hashlib.sha256(b"").hexdigest(),
                        "tracked_diff_sha256": None,
                        "tracked_diff_bytes": 0,
                        "tracked_files": [],
                        "untracked_files": [],
                    },
                ):
                    record_path = cli.start_run_record(
                        rendered,
                        "test-run",
                        environment_file=".env",
                    )
                self.assertEqual(
                    record_path,
                    root / "runs/users/bx/test-run/record.json",
                )
                usage = root / "runs/users/bx/test-run/usage"
                usage.mkdir(parents=True)
                (usage / "summary.json").write_text(
                    json.dumps(
                        {
                            "run_id": "test-run",
                            "usage": {
                                "model_tokens": 120,
                                "model_usd": 0.3,
                                "normalized_usd": 0.3,
                                "billed_usd": None,
                                "accounting_method": "gateway",
                            },
                            "evaluation": {
                                "submissions_used": 2,
                                "submissions_limit": 10,
                                "best_score": 42.0,
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                (usage / "events.jsonl").write_text(
                    json.dumps(
                        {
                            "schema_version": 1,
                            "run_id": "test-run",
                            "sequence": 1,
                            "source": "evaluator",
                            "kind": "evaluation.completed",
                            "observed_at": "2026-09-05T01:02:03Z",
                            "recorded_at": "2026-09-05T01:02:03Z",
                            "event_id": "evaluation:2",
                            "data": {
                                "operation": "score",
                                "status": "ok",
                                "score": 42.0,
                                "best_score": 42.0,
                                "submissions_used": 2,
                                "submissions_limit": 10,
                            },
                            "usage": {"normalized_usd": 0.3},
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                )
                cli.finalize_run_record(record_path, status="completed")
            finally:
                cli.REPO_ROOT = previous_root

            record = json.loads(record_path.read_text(encoding="utf-8"))
            self.assertEqual(record["data"]["status"], "completed")
            self.assertEqual(record["data"]["usage"]["model_tokens"], 120)
            self.assertEqual(record["data"]["usage"]["normalized_usd"], 0.3)
            self.assertIsNone(record["data"]["usage"]["billed_usd"])
            self.assertEqual(record["data"]["usage"]["accounting_method"], "gateway")
            self.assertEqual(
                record["data"]["metrics"]["ecdsafail_score"], 42.0
            )
            self.assertIsNotNone(record["created_at"])
            self.assertIsNotNone(record["published_at"])
            self.assertEqual(
                record["data"]["configuration"]["launcher"]["harbor_version"],
                cli.HARBOR_VERSION,
            )
            self.assertFalse(
                record["data"]["configuration"]["launcher"]
                ["environment_file_contents_recorded"]
            )
            self.assertFalse(
                record["data"]["configuration"]["launcher"]["keep_images"]
            )
            repository = record["data"]["configuration"]["repository"]
            self.assertEqual(repository["commit"], "a" * 40)
            self.assertEqual(repository["branch"], "experiment/test")
            self.assertFalse(repository["dirty"])
            self.assertTrue(repository["reproducible_from_commit"])

    def test_repository_provenance_distinguishes_clean_and_dirty_states(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def git(*arguments: str) -> None:
                subprocess.run(
                    ["git", "-C", str(root), *arguments],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

            git("init")
            git("config", "user.name", "Dungeness Test")
            git("config", "user.email", "dungeness@example.invalid")
            git("config", "commit.gpgSign", "false")
            tracked = root / "tracked.txt"
            tracked.write_text("committed\n", encoding="utf-8")
            git("add", "tracked.txt")
            git("commit", "-m", "initial")

            clean = cli.repository_provenance(root)
            self.assertTrue(clean["available"])
            self.assertEqual(len(clean["commit"]), 40)
            self.assertFalse(clean["dirty"])
            self.assertTrue(clean["reproducible_from_commit"])
            self.assertEqual(clean["tracked_files"], [])
            self.assertEqual(clean["untracked_files"], [])

            tracked.write_text("modified\n", encoding="utf-8")
            untracked = root / "run-spec.yaml"
            untracked.write_text("schema_version: 1\n", encoding="utf-8")

            dirty = cli.repository_provenance(root)
            self.assertTrue(dirty["available"])
            self.assertTrue(dirty["dirty"])
            self.assertFalse(dirty["reproducible_from_commit"])
            self.assertEqual(dirty["tracked_files"], ["tracked.txt"])
            self.assertEqual(
                [entry["path"] for entry in dirty["untracked_files"]],
                ["run-spec.yaml"],
            )
            self.assertEqual(
                dirty["untracked_files"][0]["sha256"],
                hashlib.sha256(untracked.read_bytes()).hexdigest(),
            )

    def test_run_record_uses_harbor_trial_failure_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rendered = root / "temporary-render/test-run"
            rendered.mkdir(parents=True)
            resolved = {
                "schema_version": 1,
                "id": "test-run",
                "type": "run",
                "namespace": "users/bx",
                "created_at": None,
                "published_at": None,
                "labels": {},
                "relations": {},
                "data": {
                    "run_id": "test-run",
                    "status": "planned",
                    "configuration": {
                        "sources": {},
                        "resolved": {},
                        "generated": {},
                    },
                    "metric": {
                        "name": "ecdsafail_score",
                        "direction": "minimize",
                    },
                },
            }
            (rendered / "resolved-run.json").write_text(
                json.dumps(resolved),
                encoding="utf-8",
            )

            previous_root = cli.REPO_ROOT
            cli.REPO_ROOT = root
            try:
                record_path = cli.start_run_record(rendered, "test-run")
                harbor_dir = root / "runs/users/bx/test-run/harbor/test-run"
                harbor_dir.mkdir(parents=True)
                (harbor_dir / "result.json").write_text(
                    json.dumps(
                        {
                            "id": "job-id",
                            "stats": {
                                "n_errored_trials": 1,
                                "n_cancelled_trials": 0,
                                "n_running_trials": 0,
                                "n_pending_trials": 0,
                                "evals": {
                                    "codex__kimi": {
                                        "exception_stats": {
                                            "AgentTimeoutError": ["trial-id"]
                                        }
                                    }
                                },
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                cli.finalize_run_record(record_path, status="completed")
            finally:
                cli.REPO_ROOT = previous_root

            record = json.loads(record_path.read_text(encoding="utf-8"))
            self.assertEqual(record["data"]["status"], "failed")
            self.assertEqual(
                record["data"]["error"],
                "Harbor reported 1 errored trial: AgentTimeoutError",
            )

    def test_temporary_render_is_removed_or_retained_under_run(self) -> None:
        run_id = "test-run"
        with tempfile.TemporaryDirectory() as run_directory:
            run_dir = Path(run_directory) / "runs" / run_id

            removable_root = Path(
                tempfile.mkdtemp(
                    prefix=f"dungeness-{run_id}-",
                    dir=tempfile.gettempdir(),
                )
            )
            removable = removable_root / "task"
            removable.mkdir()
            cli.dispose_render(removable, run_id, run_dir, keep=False)
            self.assertFalse(removable_root.exists())

            retained_root = Path(
                tempfile.mkdtemp(
                    prefix=f"dungeness-{run_id}-",
                    dir=tempfile.gettempdir(),
                )
            )
            retained = retained_root / "task"
            retained.mkdir()
            (retained / "task.toml").write_text("schema_version = 1\n")
            retained_path = cli.dispose_render(
                retained,
                run_id,
                run_dir,
                keep=True,
            )
            self.assertEqual(
                retained_path,
                run_dir / "debug" / "harbor-task",
            )
            self.assertTrue((retained_path / "task.toml").is_file())
            self.assertFalse(retained_root.exists())

    def test_prune_permanently_removes_unreferenced_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir = root / "runs" / "users" / "bx" / "old-run"
            run_dir.mkdir(parents=True)
            (run_dir / "record.json").write_text(
                json.dumps(
                    {
                        "id": "old-run",
                        "type": "run",
                        "namespace": "users/bx",
                        "relations": {},
                        "data": {"run_id": "old-run"},
                    }
                ),
                encoding="utf-8",
            )
            (run_dir / "output.txt").write_text("result", encoding="utf-8")

            previous_root = cli.REPO_ROOT
            cli.REPO_ROOT = root
            try:
                result = cli.prune_run(
                    cli.argparse.Namespace(run_id="old-run", yes=True)
                )
            finally:
                cli.REPO_ROOT = previous_root

            self.assertEqual(result, 0)
            self.assertFalse(run_dir.exists())

    def test_runs_lists_records_linked_to_run_spec(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_spec = root / "run-spec.yaml"
            write_run_spec(run_spec)
            runs_root = root / "runs" / "users" / "bx"
            for run_id, status, effort, score in (
                ("run-low", "completed", "low", 123),
                ("run-high", "cancelled", "high", None),
            ):
                run_dir = runs_root / run_id
                run_dir.mkdir(parents=True)
                (run_dir / "record.json").write_text(
                    json.dumps(
                        {
                            "schema_version": 1,
                            "id": run_id,
                            "type": "run",
                            "namespace": "users/bx",
                            "created_at": f"2026-08-20T00:00:0{1 if effort == 'low' else 2}Z",
                            "labels": {"reasoning_effort": effort},
                            "relations": {
                                "run_spec": (
                                    "run-spec:users/bx/ecdsa-fail-command-1usd"
                                )
                            },
                            "data": {
                                "run_id": run_id,
                                "status": status,
                                "metric": {"name": "ecdsafail_score"},
                                "metrics": (
                                    {"ecdsafail_score": score}
                                    if score is not None
                                    else {}
                                ),
                                "started_at": (
                                    f"2026-08-20T00:00:"
                                    f"0{1 if effort == 'low' else 2}Z"
                                ),
                            },
                        }
                    ),
                    encoding="utf-8",
                )

            previous_root = cli.REPO_ROOT
            cli.REPO_ROOT = root
            try:
                with patch("builtins.print") as output:
                    result = cli.list_runs(
                        cli.argparse.Namespace(
                            target=str(run_spec),
                            latest=False,
                            json=False,
                        )
                    )
            finally:
                cli.REPO_ROOT = previous_root

            rendered = "\n".join(
                " ".join(str(value) for value in call.args)
                for call in output.call_args_list
            )
            self.assertEqual(result, 0)
            self.assertIn("run-low", rendered)
            self.assertIn("123", rendered)
            self.assertIn("run-high", rendered)
            self.assertIn("cancelled", rendered)

    def test_prune_refuses_run_referenced_by_another_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "runs" / "parent-run"
            child = root / "runs" / "child-run"
            target.mkdir(parents=True)
            child.mkdir(parents=True)
            (target / "record.json").write_text(
                json.dumps(
                    {
                        "id": "parent-run",
                        "type": "run",
                        "namespace": "users/bx",
                        "relations": {},
                        "data": {"run_id": "parent-run"},
                    }
                ),
                encoding="utf-8",
            )
            (child / "record.json").write_text(
                json.dumps(
                    {
                        "id": "child-run",
                        "type": "run",
                        "namespace": "users/bx",
                        "relations": {
                            "resumed_from": "run:users/bx/parent-run",
                        },
                        "data": {"run_id": "child-run"},
                    }
                ),
                encoding="utf-8",
            )

            previous_root = cli.REPO_ROOT
            cli.REPO_ROOT = root
            try:
                with self.assertRaisesRegex(SystemExit, "child-run"):
                    cli.prune_run(
                        cli.argparse.Namespace(run_id="parent-run", yes=True)
                    )
            finally:
                cli.REPO_ROOT = previous_root

            self.assertTrue(target.exists())

    def test_prune_cancellation_and_run_id_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir = root / "runs" / "keep-run"
            run_dir.mkdir(parents=True)

            previous_root = cli.REPO_ROOT
            cli.REPO_ROOT = root
            try:
                with patch("builtins.input", return_value="no"):
                    self.assertEqual(
                        cli.prune_run(
                            cli.argparse.Namespace(run_id="keep-run", yes=False)
                        ),
                        0,
                    )
                with self.assertRaisesRegex(SystemExit, "1-128"):
                    cli.prune_run(
                        cli.argparse.Namespace(run_id="../keep-run", yes=True)
                    )
            finally:
                cli.REPO_ROOT = previous_root

            self.assertTrue(run_dir.exists())

    def test_verifier_resolves_candidate_path_and_run_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dockerfile = root / "Dockerfile"
            dockerfile.write_text(
                "ENV CANDIDATE_PATH=/workspace/repo/src/point_add \\\n"
                "    SCORE_PATH=/logs/verifier/score.json\n",
                encoding="utf-8",
            )
            relative = cli.verifier_candidate_path(dockerfile)
            self.assertEqual(relative.as_posix(), "src/point_add")

            run_dir = root / "runs/test-run"
            artifact = (
                run_dir
                / "harbor/job/trial/artifacts/workspace/repo/src/point_add"
            )
            artifact.mkdir(parents=True)
            task_root = run_dir / "debug/harbor-task"
            self.assertEqual(
                cli.resolve_verification_candidate(
                    run_dir,
                    task_root,
                    relative,
                    None,
                ),
                artifact.resolve(),
            )

    def test_verifier_memory_defaults_to_retained_task_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            task_root = Path(directory)
            (task_root / "task.toml").write_text(
                "[verifier.environment]\nmemory_mb = 8192\n",
                encoding="utf-8",
            )
            self.assertEqual(
                cli.retained_verifier_memory(task_root),
                "8192m",
            )
            (task_root / "task.toml").unlink()
            self.assertEqual(cli.retained_verifier_memory(task_root), "20g")










if __name__ == "__main__":
    unittest.main()
