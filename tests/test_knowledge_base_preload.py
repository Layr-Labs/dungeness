from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_BASE_REF = "knowledge-base:users/bx/contaminated/ecdsa-paper-kb-v1"
KNOWLEDGE_BASE_PROMPT_PROFILE = (
    "knowledge-base-prompt-profile:system/dungeness/ecdsa-paper-v1"
)
EIGHT_PAPER_KNOWLEDGE_BASE_REF = (
    "knowledge-base:users/bx/contaminated/ecdsa-8-paper-kb-v1"
)
EIGHT_PAPER_PROMPT_PROFILE = (
    "knowledge-base-prompt-profile:system/dungeness/ecdsa-8-paper-v1"
)
RAW_PAPER_KNOWLEDGE_BASE_REF = (
    "knowledge-base:users/bx/ecdsa-schrottenloher-raw-paper-v1"
)
RAW_PAPER_PROMPT_PROFILE = (
    "knowledge-base-prompt-profile:system/dungeness/raw-paper-read-only-v1"
)
RAW_PAPER_SHA256 = (
    "8744ef6db6c60b62d952a1dd24e5bd433242af970f4755c8b49b020a731584af"
)
RAW_EIGHT_PAPER_KNOWLEDGE_BASE_REF = (
    "knowledge-base:users/bx/ecdsa-8-raw-paper-kb-v1"
)
RAW_EIGHT_PAPER_PROMPT_PROFILE = (
    "knowledge-base-prompt-profile:system/dungeness/"
    "raw-paper-corpus-read-only-v1"
)
RAW_EIGHT_PAPER_DOCUMENTS = {
    "2020-077.pdf": (
        22,
        "ed7daaba41f3a6d2a42536b977a91a97e343a23a9f0d9324d3b9aaf3eb0848c2",
    ),
    "2110.08973v3.pdf": (
        25,
        "13ee62c1108a9a2bd9654235f6ad6cffe30660c35f524b60dd54a38af8d18997",
    ),
    "2407.20167v1.pdf": (
        45,
        "c5b152e5dbfdbc767e49edaec45f3550e623fdefa269fdabed0ab578d7a392f0",
    ),
    "2410.00899v1.pdf": (
        6,
        "5da56cc0dd20b0afe73b3d0a188ba7e0e9826960c37b9b972671520755a74713",
    ),
    "2507.23079v1.pdf": (
        8,
        "31c8fb8d52329c79cd29816d8c22087d5e84aa6fee46458f1f5c0ef726adba3f",
    ),
    "2510.10967v1.pdf": (
        52,
        "dcbbd0034ebcc3918a31ecc211ab108ec3a11d02840a78f504f915b73a5370ca",
    ),
    "2606.02235v1.pdf": (
        19,
        RAW_PAPER_SHA256,
    ),
    "2607.13816v2.pdf": (
        50,
        "8e61e2ce2be1a9a9404c67fe2b42b1e381093e215ada2e20ce3f2de925938901",
    ),
}


def load_module(name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


cli = load_module("dungeness_kb_cli", REPOSITORY_ROOT / "dungeness")
build = load_module(
    "dungeness_kb_build",
    REPOSITORY_ROOT / "adapters/harbor/build.py",
)


def missing_markdown_links(root: Path) -> list[tuple[str, str]]:
    missing = []
    for page in root.rglob("*.md"):
        for target in re.findall(
            r"\[[^\]]*\]\(([^)]+)\)",
            page.read_text(encoding="utf-8"),
        ):
            if target.startswith(("http://", "https://", "#")):
                continue
            relative = target.split("#", 1)[0]
            if not (page.parent / relative).resolve().exists():
                missing.append((page.relative_to(root).as_posix(), target))
    return missing


class KnowledgeBasePreloadTests(unittest.TestCase):
    def test_raw_single_paper_run_exposes_only_the_unchanged_pdf(self) -> None:
        path = (
            REPOSITORY_ROOT
            / "run-specs/users/bx/"
            "ecdsa-astra-high-raw-schrottenloher-paper-12usd/"
            "ecdsa-astra-high-raw-schrottenloher-paper-12usd.yaml"
        )
        _, document = cli.load_run_spec(str(path))
        configured = document["initialization"]["knowledge_base"]
        self.assertEqual(
            configured["ref"],
            RAW_PAPER_KNOWLEDGE_BASE_REF,
        )
        self.assertEqual(
            configured["prompt_profile"],
            RAW_PAPER_PROMPT_PROFILE,
        )
        self.assertEqual(configured["layers"], ["raw_paper"])

        preload = build.resolve_knowledge_base_preload(configured)
        assert preload is not None
        self.assertEqual(
            list(preload["files"]),
            ["2606.02235v1.pdf"],
        )
        self.assertEqual(
            preload["interface"],
            {
                "mode": "raw-document-read-only-v1",
                "operations": ["read"],
            },
        )
        self.assertFalse(preload["behavior_feedback"]["enabled"])
        self.assertEqual(preload["behavior_feedback"]["mode"], "off")
        source = preload["files"]["2606.02235v1.pdf"]
        self.assertEqual(
            build.hashlib.sha256(source.read_bytes()).hexdigest(),
            RAW_PAPER_SHA256,
        )

        prompt_path, profile, resolved_prompt = (
            build.resolve_knowledge_base_prompt_profile(
                RAW_PAPER_PROMPT_PROFILE
            )
        )
        assert prompt_path is not None
        assert profile is not None
        assert resolved_prompt is not None
        self.assertEqual(prompt_path.name, "raw-paper-read-only-v1.yaml")
        self.assertEqual(
            resolved_prompt["mode"],
            "raw-paper-read-only-v1",
        )
        notice = build.build_knowledge_base_notice(
            profile,
            {
                "ref": RAW_PAPER_KNOWLEDGE_BASE_REF,
                "entrypoint": "2606.02235v1.pdf",
                "page_count": 19,
            },
        )
        self.assertIn(
            "`knowledge-base read 2606.02235v1.pdf --pages 1-5`",
            notice,
        )
        self.assertIn("through page 19", notice)
        self.assertIn("has not been summarized", notice)
        self.assertIn("deliberately unavailable", notice)
        self.assertNotIn("`knowledge-base search", notice)
        self.assertNotIn("`knowledge-base inspire", notice)

        with tempfile.TemporaryDirectory() as directory:
            service = Path(directory) / "knowledge-base"
            service.mkdir()
            resolved = build.materialize_knowledge_base_service(
                preload,
                service,
            )
            target = service / "content"
            paper = target / "2606.02235v1.pdf"
            self.assertEqual(paper.read_bytes(), source.read_bytes())
            self.assertEqual(
                build.hashlib.sha256(paper.read_bytes()).hexdigest(),
                RAW_PAPER_SHA256,
            )
            self.assertEqual(
                resolved["interface"],
                {
                    "mode": "raw-document-read-only-v1",
                    "operations": ["read"],
                },
            )
            self.assertEqual(resolved["page_count"], 19)
            runtime_manifest = yaml.safe_load(
                (target / "knowledge-base.yaml").read_text(encoding="utf-8")
            )
            self.assertEqual(
                runtime_manifest["interface"]["operations"],
                ["read"],
            )

            web = {
                "historical_cutoff": {
                    "end_published_date": "2026-01-01T00:00:00Z"
                },
                "search": {"max_results": 10},
            }
            budget = {
                "web": {"searches": 10, "fetches": 10},
                "model": {"requests": 10, "total_tokens": 1000},
                "evaluation": {"submissions": 10},
            }
            compose = yaml.safe_load(
                build.build_compose(
                    "raw-paper-test",
                    web,
                    budget,
                    provider="openai",
                    knowledge_base=resolved,
                )
            )
            self.assertEqual(
                compose["services"]["main"]["environment"][
                    "DUNGENESS_KNOWLEDGE_BASE_OPERATIONS"
                ],
                "read",
            )

    def test_raw_eight_paper_run_exposes_only_unchanged_pdfs(self) -> None:
        path = (
            REPOSITORY_ROOT
            / "run-specs/users/bx/ecdsa-astra-high-raw-8-paper-12usd/"
            "ecdsa-astra-high-raw-8-paper-12usd.yaml"
        )
        _, document = cli.load_run_spec(str(path))
        configured = document["initialization"]["knowledge_base"]
        self.assertEqual(
            configured["ref"],
            RAW_EIGHT_PAPER_KNOWLEDGE_BASE_REF,
        )
        self.assertEqual(
            configured["prompt_profile"],
            RAW_EIGHT_PAPER_PROMPT_PROFILE,
        )
        self.assertEqual(configured["layers"], ["raw_papers"])

        preload = build.resolve_knowledge_base_preload(configured)
        assert preload is not None
        self.assertEqual(
            list(preload["files"]),
            sorted(RAW_EIGHT_PAPER_DOCUMENTS),
        )
        self.assertEqual(
            preload["interface"],
            {
                "mode": "raw-document-corpus-read-only-v1",
                "operations": ["read"],
            },
        )
        self.assertFalse(preload["behavior_feedback"]["enabled"])
        self.assertEqual(preload["behavior_feedback"]["mode"], "off")
        self.assertEqual(len(preload["documents"]), 8)
        for relative, (pages, expected_sha256) in (
            RAW_EIGHT_PAPER_DOCUMENTS.items()
        ):
            source = preload["files"][relative]
            self.assertEqual(
                build.hashlib.sha256(source.read_bytes()).hexdigest(),
                expected_sha256,
            )
            resolved_document = next(
                item
                for item in preload["documents"]
                if item["path"] == relative
            )
            self.assertEqual(resolved_document["pages"], pages)

        prompt_path, profile, resolved_prompt = (
            build.resolve_knowledge_base_prompt_profile(
                RAW_EIGHT_PAPER_PROMPT_PROFILE
            )
        )
        assert prompt_path is not None
        assert profile is not None
        assert resolved_prompt is not None
        self.assertEqual(
            prompt_path.name,
            "raw-paper-corpus-read-only-v1.yaml",
        )
        self.assertEqual(
            resolved_prompt["mode"],
            "raw-paper-corpus-read-only-v1",
        )

        with tempfile.TemporaryDirectory() as directory:
            service = Path(directory) / "knowledge-base"
            service.mkdir()
            resolved = build.materialize_knowledge_base_service(
                preload,
                service,
            )
            target = service / "content"
            self.assertEqual(resolved["document_count"], 8)
            self.assertEqual(resolved["total_page_count"], 227)
            self.assertIsNone(resolved["page_count"])
            self.assertEqual(
                resolved["interface"],
                {
                    "mode": "raw-document-corpus-read-only-v1",
                    "operations": ["read"],
                },
            )
            for relative, (_, expected_sha256) in (
                RAW_EIGHT_PAPER_DOCUMENTS.items()
            ):
                paper = target / relative
                self.assertTrue(paper.is_file())
                self.assertEqual(
                    build.hashlib.sha256(paper.read_bytes()).hexdigest(),
                    expected_sha256,
                )

            notice = build.build_knowledge_base_notice(profile, resolved)
            self.assertIn("The 8 complete original papers", notice)
            self.assertIn("Together they contain\n227 pages", notice)
            self.assertIn(
                "`knowledge-base read 2606.02235v1.pdf --pages 1-5`",
                notice,
            )
            self.assertIn(
                "`knowledge-base read 2510.10967v1.pdf --pages 51-52`",
                notice,
            )
            self.assertIn(
                "`knowledge-base read 2020-077.pdf --pages 21-22`",
                notice,
            )
            self.assertEqual(notice.count("`knowledge-base read "), 48)
            self.assertIn("have not been summarized", notice)
            self.assertIn("deliberately unavailable", notice)
            self.assertNotIn("`knowledge-base search", notice)
            self.assertNotIn("`knowledge-base inspire", notice)

    def test_eight_paper_run_spec_materializes_complete_sidecar(self) -> None:
        path = (
            REPOSITORY_ROOT
            / "run-specs/users/bx/contaminated/"
            "ecdsa-gpt56-high-kb-8-paper-12usd/"
            "ecdsa-gpt56-high-kb-8-paper-12usd.yaml"
        )
        _, document = cli.load_run_spec(str(path))
        configured = document["initialization"]["knowledge_base"]
        self.assertEqual(configured["ref"], EIGHT_PAPER_KNOWLEDGE_BASE_REF)
        self.assertEqual(
            configured["prompt_profile"],
            EIGHT_PAPER_PROMPT_PROFILE,
        )
        self.assertEqual(
            configured["layers"],
            ["eight_paper_knowledge_base"],
        )

        preload = build.resolve_knowledge_base_preload(configured)
        assert preload is not None
        self.assertEqual(len(preload["files"]), 153)

        prompt_path, profile, resolved_prompt = (
            build.resolve_knowledge_base_prompt_profile(
                EIGHT_PAPER_PROMPT_PROFILE
            )
        )
        assert prompt_path is not None
        assert profile is not None
        assert resolved_prompt is not None
        self.assertEqual(prompt_path.name, "ecdsa-8-paper-v1.yaml")
        notice = build.build_knowledge_base_notice(
            profile,
            {
                "ref": EIGHT_PAPER_KNOWLEDGE_BASE_REF,
                "access_mode": "sidecar",
                "service_url": "http://knowledge-base:8078",
                "entrypoint": "index.md",
            },
        )
        self.assertIn("## ECDSA eight-paper knowledge-base inspiration", notice)
        self.assertIn("`paper-matrix.md`", notice)
        self.assertIn("`experiment-map.md`", notice)

        with tempfile.TemporaryDirectory() as directory:
            service = Path(directory) / "knowledge-base"
            service.mkdir()
            resolved = build.materialize_knowledge_base_service(
                preload,
                service,
            )
            target = service / "content"
            for source in (
                "2020-077.md",
                "2110.08973.md",
                "2407.20167.md",
                "2410.00899.md",
                "2507.23079.md",
                "2510.10967.md",
                "2606.02235.md",
                "2607.13816.md",
            ):
                self.assertTrue((target / "sources" / source).is_file())
            self.assertTrue((target / "paper-matrix.md").is_file())
            self.assertTrue((target / "experiment-map.md").is_file())
            self.assertEqual(
                resolved["layers"],
                ["eight_paper_knowledge_base"],
            )
            self.assertEqual(missing_markdown_links(target), [])

    def test_configured_run_spec_resolves_static_knowledge_base(self) -> None:
        path = (
            REPOSITORY_ROOT
            / "run-specs/users/bx/contaminated/"
            "ecdsa-kimi-subscription-llm-wiki-max-12usd/"
            "ecdsa-kimi-subscription-llm-wiki-max-12usd-knowledge-base.yaml"
        )
        _, document = cli.load_run_spec(str(path))
        configured = document["initialization"]["knowledge_base"]
        self.assertEqual(configured["ref"], KNOWLEDGE_BASE_REF)
        self.assertEqual(configured["access"], "sidecar")
        self.assertEqual(
            configured["prompt_profile"],
            KNOWLEDGE_BASE_PROMPT_PROFILE,
        )
        self.assertEqual(
            configured["layers"],
            ["paper_knowledge_base"],
        )
        resolved = cli.resolve_run_spec_arguments(
            cli.argparse.Namespace(
                target=str(path),
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
                agent_timeout_sec=None,
            )
        )
        self.assertEqual(resolved.task, "ecdsa-fail-v2")
        self.assertEqual(
            resolved.run_spec_ref,
            "run-spec:users/bx/"
            "ecdsa-kimi-subscription-llm-wiki-max-12usd-knowledge-base",
        )

    def test_cli_rejects_unknown_layer(self) -> None:
        with self.assertRaisesRegex(SystemExit, "unknown knowledge-base layers"):
            cli.validate_run_spec_knowledge_base(
                {
                    "initialization": {
                        "knowledge_base": {
                            "ref": KNOWLEDGE_BASE_REF,
                            "layers": ["missing"],
                        }
                    }
                }
            )

    def test_prompt_profile_resolves_file_backed_contract(self) -> None:
        path, profile, resolved = build.resolve_knowledge_base_prompt_profile(
            KNOWLEDGE_BASE_PROMPT_PROFILE
        )
        assert path is not None
        assert profile is not None
        assert resolved is not None
        self.assertEqual(path.name, "ecdsa-paper-v1.yaml")
        self.assertEqual(profile["type"], "knowledge-base-prompt-profile")
        self.assertEqual(resolved["mode"], "kb-carrot-stick-v1")
        notice = build.build_knowledge_base_notice(
            profile,
            {
                "ref": KNOWLEDGE_BASE_REF,
                "access_mode": "sidecar",
                "service_url": "http://knowledge-base:8078",
                "entrypoint": "index.md",
            },
        )
        self.assertIn("## ECDSA paper knowledge-base inspiration", notice)
        self.assertIn("### Startup orientation", notice)
        self.assertIn("`knowledge-base read README.md`", notice)
        self.assertIn("`knowledge-base read AGENTS.md`", notice)
        self.assertIn("`knowledge-base read index.md`", notice)
        self.assertIn("sidecar performs ripgrep", notice)
        self.assertIn("`knowledge-base inspire", notice)
        self.assertIn("planned candidate change", notice)
        self.assertIn("Do not pipe,\nredirect", notice)
        self.assertNotIn("MCP", notice)
        self.assertNotIn("{entrypoint}", notice)

    def test_full_projection_materializes_in_sidecar_with_provenance(self) -> None:
        preload = build.resolve_knowledge_base_preload(
            {"ref": KNOWLEDGE_BASE_REF}
        )
        assert preload is not None
        with tempfile.TemporaryDirectory() as directory:
            service = Path(directory) / "knowledge-base"
            service.mkdir()
            resolved = build.materialize_knowledge_base_service(
                preload,
                service,
            )
            target = service / "content"
            runtime_manifest = yaml.safe_load(
                (target / "knowledge-base.yaml").read_text(encoding="utf-8")
            )
            self.assertEqual(runtime_manifest["preload"]["status"], "injected")
            self.assertEqual(
                runtime_manifest["preload"]["source_ref"],
                KNOWLEDGE_BASE_REF,
            )
            self.assertEqual(resolved["access_mode"], "sidecar")
            self.assertEqual(
                resolved["service_url"],
                "http://knowledge-base:8078",
            )
            self.assertEqual(resolved["entrypoint"], "index.md")
            self.assertTrue((target / "index.md").is_file())
            self.assertTrue((target / "concepts/hypotheses.md").is_file())
            self.assertEqual(missing_markdown_links(target), [])
            self.assertEqual(len(resolved["source_sha256"]), 64)
            self.assertEqual(len(resolved["injected_sha256"]), 64)

    def test_explicit_archive_layer_materializes_full_sidecar_projection(self) -> None:
        preload = build.resolve_knowledge_base_preload(
            {
                "ref": KNOWLEDGE_BASE_REF,
                "layers": ["paper_knowledge_base"],
            }
        )
        assert preload is not None
        with tempfile.TemporaryDirectory() as directory:
            service = Path(directory) / "knowledge-base"
            service.mkdir()
            resolved = build.materialize_knowledge_base_service(
                preload,
                service,
            )
            target = service / "content"
            index = (target / "index.md").read_text(encoding="utf-8")
            self.assertIn("# Index", index)
            self.assertTrue((target / "nodes/benchmark-adaptation.md").exists())
            self.assertTrue((target / "sources/companion-code-map.md").exists())
            self.assertEqual(resolved["layers"], ["paper_knowledge_base"])
            self.assertEqual(missing_markdown_links(target), [])

    def test_compose_exposes_sidecar_without_workspace_mount(self) -> None:
        web = {
            "historical_cutoff": {
                "end_published_date": "2026-01-01T00:00:00Z"
            },
            "search": {"max_results": 10},
        }
        budget = {
            "web": {"searches": 10, "fetches": 10},
            "model": {"requests": 10, "total_tokens": 1000},
            "evaluation": {"submissions": 10},
        }
        document = yaml.safe_load(
            build.build_compose(
                "test-run",
                web,
                budget,
                provider="openai",
                knowledge_base={"access_mode": "sidecar"},
            )
        )
        self.assertIn("knowledge-base", document["services"])
        main = document["services"]["main"]
        self.assertEqual(
            main["environment"]["DUNGENESS_KNOWLEDGE_BASE_URL"],
            "http://knowledge-base:8078",
        )
        self.assertNotIn("volumes", main)
        self.assertIn(
            "http://localhost:8078/healthz",
            document["services"]["knowledge-base"]["healthcheck"]["test"][-1],
        )

    def test_preload_rejects_workspace_destination(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown.*destination"):
            build.resolve_knowledge_base_preload(
                {
                    "ref": KNOWLEDGE_BASE_REF,
                    "destination": "../knowledge-base",
                }
            )

    def test_projection_rejects_dangling_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.md").write_text(
                "[Missing](missing.md)\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "missing or escaping links"):
                build._validate_knowledge_base_links(root)


if __name__ == "__main__":
    unittest.main()
