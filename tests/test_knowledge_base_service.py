from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "knowledge_base_service",
    REPOSITORY_ROOT / "services/knowledge-base/server.py",
)
assert SPEC is not None and SPEC.loader is not None
service_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(service_module)


class KnowledgeBaseServiceTests(unittest.TestCase):
    def make_service(
        self,
        directory: str,
        *,
        feedback: bool = True,
        concrete_sources_only: bool = False,
        interface_operations: list[str] | None = None,
    ):
        root = Path(directory) / "content"
        usage = Path(directory) / "usage"
        (root / "nodes").mkdir(parents=True)
        (root / ".dungeness-knowledge-base.json").write_text(
            json.dumps(
                {
                    "source_ref": "knowledge-base:users/bx/test-v1",
                    "entrypoint": "index.md",
                    "selected_layers": ["paper"],
                    "source_sha256": "1" * 64,
                    "injected_sha256": "2" * 64,
                }
            ),
            encoding="utf-8",
        )
        (root / "index.md").write_text(
            "# Index\n\n[Point](nodes/point.md)\n",
            encoding="utf-8",
        )
        (root / "nodes/field.md").write_text(
            "---\nid: field\n---\n\n# Field Arithmetic\n",
            encoding="utf-8",
        )
        (root / "nodes/point.md").write_text(
            "---\nid: point\ndepends_on: [field]\n---\n\n"
            "# Point Addition\n\nReduce inversion live width.\n",
            encoding="utf-8",
        )
        (root / "nodes/schedule.md").write_text(
            "---\nid: schedule\ndepends_on: [point]\n---\n\n# Schedule\n",
            encoding="utf-8",
        )
        (root / "knowledge-base.yaml").write_text(
            "schema_version: 1\n"
            "type: knowledge-base\n"
            "namespace: users/bx\n"
            "id: test-v1\n"
            + (
                "interface:\n"
                "  mode: test\n"
                "  operations:\n"
                + "".join(
                    f"    - {operation}\n"
                    for operation in interface_operations
                )
                if interface_operations is not None
                else ""
            )
            + (
                "behavior_feedback:\n"
                "  qualifying_sources:\n"
                "    prefixes: [nodes/]\n"
                "    pages: []\n"
                if concrete_sources_only
                else ""
            ),
            encoding="utf-8",
        )
        return service_module.KnowledgeBaseService(
            root,
            usage,
            "test-run",
            behavior_feedback_config={
                "enabled": feedback,
                "mode": "visible",
            },
        )

    def test_search_returns_bounded_citable_passages_and_logs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(directory)
            search = service.search("live width", 8, 3)
            self.assertEqual(search["results"][0]["source"], "nodes/point.md")
            self.assertEqual(search["results"][0]["line_start"], 5)
            self.assertIn("Reduce inversion live width", search["results"][0]["text"])
            events = [
                json.loads(line)
                for line in (
                    Path(directory) / "usage/events.jsonl"
                ).read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(
                [
                    event["data"]["action"]
                    for event in events
                    if event.get("kind") == "knowledge_base.request"
                ],
                ["search"],
            )

    def test_search_ors_terms_and_ranks_by_distinct_term_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(directory)
            # "callback" appears nowhere in the corpus. All-terms semantics
            # would return nothing; the tool must still surface the passages
            # that name the terms it does have, best match first.
            search = service.search("inversion width callback", 8, 1)
            self.assertEqual(search["status"], "matches")
            best = search["results"][0]
            self.assertEqual(best["source"], "nodes/point.md")
            self.assertEqual(best["match_terms"], ["inversion", "width"])
            self.assertTrue(
                all(
                    len(result["match_terms"])
                    <= len(best["match_terms"])
                    for result in search["results"]
                )
            )

    def test_search_labels_and_prefers_qualifying_sources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(
                directory,
                concrete_sources_only=True,
            )
            # "Point" appears in both index.md (orientation) and
            # nodes/point.md (qualifying) with one matched term each.
            search = service.search("Point", 8, 0)
            self.assertEqual(search["results"][0]["source"], "nodes/point.md")
            self.assertTrue(search["results"][0]["qualifying_source"])
            self.assertFalse(
                next(
                    result
                    for result in search["results"]
                    if result["source"] == "index.md"
                )["qualifying_source"]
            )

    def test_search_treats_query_as_literal_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(directory)
            # A regex would match "Point Addition"; a literal substring must
            # not, so punctuation in a query can never be a hidden operator.
            self.assertEqual(
                service.search("P.int", 8, 0)["status"],
                "no_matches",
            )
            self.assertEqual(
                service.search("Point", 8, 0)["status"],
                "matches",
            )

    def test_inspiration_must_reference_exact_new_search_passage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(directory)
            search = service.search("live width", 8, 3)
            result = search["results"][0]
            passage = {
                "source": result["source"],
                "line_start": result["line_start"],
                "line_end": result["line_end"],
            }
            first = service.record_inspiration(
                search["search_id"],
                [passage],
                "Reduce the live inversion width.",
                "Reuse a freed register in the inversion callback.",
            )
            self.assertTrue(first["qualifying"])
            duplicate = service.record_inspiration(
                search["search_id"],
                [passage],
                "Repeat the same idea.",
                "Repeat the same candidate change.",
            )
            self.assertFalse(duplicate["qualifying"])
            self.assertEqual(duplicate["reason"], "duplicate_passages_only")

            invalid = dict(passage)
            invalid["line_end"] += 1
            with self.assertRaisesRegex(
                service_module.KnowledgeBaseError,
                "exactly match",
            ):
                service.record_inspiration(
                    search["search_id"],
                    [invalid],
                    "Invalid range.",
                    "Should be rejected.",
                )

    def test_ecdsa_style_filter_rejects_generic_orientation_passage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(
                directory,
                concrete_sources_only=True,
            )
            search = service.search("Index", 8, 0)
            result = search["results"][0]
            lookup = service.record_inspiration(
                search["search_id"],
                [{
                    "source": result["source"],
                    "line_start": result["line_start"],
                    "line_end": result["line_end"],
                }],
                "The index points toward point addition.",
                "Inspect the point implementation.",
            )
            self.assertFalse(lookup["qualifying"])
            self.assertEqual(
                lookup["reason"],
                "no_implementation_detail_passage",
            )
            self.assertEqual(lookup["implementation_passage_count"], 0)
            # A rejection must say which sources would have qualified, so the
            # agent can retry instead of concluding the corpus is unusable.
            self.assertEqual(lookup["qualifying_sources"], ["nodes/"])

    def test_missing_takeaway_cannot_qualify(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(directory)
            search = service.search("live width", 8, 3)
            result = search["results"][0]
            with self.assertRaisesRegex(
                service_module.KnowledgeBaseError,
                "takeaway",
            ):
                service.record_inspiration(
                    search["search_id"],
                    [{
                        "source": result["source"],
                        "line_start": result["line_start"],
                        "line_end": result["line_end"],
                    }],
                    "",
                    "Reuse a freed register.",
                )

    def test_neighbors_returns_dependencies_and_reverse_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(directory)
            result = service.neighbors("point")
            self.assertEqual(result["depends_on"], ["field"])
            self.assertEqual(result["required_by"], ["schedule"])

    def test_status_exposes_versioned_interface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(directory)
            status = service.status()
            self.assertEqual(
                status["source_ref"],
                "knowledge-base:users/bx/test-v1",
            )
            self.assertEqual(
                status["interface"]["transport"],
                "HTTP JSON",
            )
            self.assertEqual(
                status["interface"]["endpoints"]["inspire"],
                "POST /v1/inspire",
            )

    def test_read_only_interface_rejects_every_other_operation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(
                directory,
                interface_operations=["read"],
            )
            self.assertIn("# Index", service.read("index.md")["content"])
            for operation in (
                service.status,
                service.list_pages,
                lambda: service.search("point"),
                lambda: service.neighbors("point"),
                lambda: service.record_inspiration(
                    "search",
                    [],
                    "takeaway",
                    "change",
                ),
            ):
                with self.subTest(operation=operation):
                    with self.assertRaisesRegex(
                        service_module.KnowledgeBaseAccessError,
                        "operation is disabled",
                    ):
                        operation()

    def test_pdf_is_rendered_only_when_read(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "content"
            usage = Path(directory) / "usage"
            root.mkdir()
            (root / "paper.pdf").write_bytes(b"%PDF-1.7\nraw-paper")
            (root / ".dungeness-knowledge-base.json").write_text(
                json.dumps(
                    {
                        "source_ref": "knowledge-base:users/bx/raw-paper",
                        "entrypoint": "paper.pdf",
                    }
                ),
                encoding="utf-8",
            )
            (root / "knowledge-base.yaml").write_text(
                "schema_version: 1\n"
                "type: knowledge-base\n"
                "namespace: users/bx\n"
                "id: raw-paper\n"
                "title: Raw Paper\n"
                "entrypoint: paper.pdf\n"
                "interface:\n"
                "  mode: raw-document-read-only-v1\n"
                "  operations: [read]\n",
                encoding="utf-8",
            )
            service = service_module.KnowledgeBaseService(
                root,
                usage,
                "test-run",
                behavior_feedback_config={
                    "enabled": False,
                    "mode": "off",
                },
            )
            with patch.object(
                service_module.subprocess,
                "run",
                return_value=service_module.subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout=b"Complete paper text.\n",
                    stderr=b"",
                ),
            ) as run:
                result = service.read("paper.pdf", 1, 5)
            self.assertEqual(result["content"], "Complete paper text.\n")
            self.assertEqual(result["format"], "pdf")
            self.assertEqual(result["renderer"], "pdftotext-layout")
            self.assertEqual(
                result["page_window"],
                {"first": 1, "last": 5},
            )
            self.assertEqual(
                result["content_sha256"],
                service_module.hashlib.sha256(
                    b"Complete paper text.\n"
                ).hexdigest(),
            )
            command = run.call_args.args[0]
            self.assertEqual(command[0], "pdftotext")
            self.assertIn("-layout", command)
            self.assertEqual(
                command[command.index("-f") : command.index("-f") + 4],
                ["-f", "1", "-l", "5"],
            )
            event = json.loads(
                (usage / "events.jsonl").read_text(encoding="utf-8")
            )
            self.assertEqual(event["data"]["action"], "read")
            self.assertEqual(
                event["data"]["renderer"],
                "pdftotext-layout",
            )
            self.assertEqual(
                event["data"]["content_sha256"],
                result["content_sha256"],
            )
            self.assertEqual(
                event["data"]["page_window"],
                {"first": 1, "last": 5},
            )

    def test_page_window_is_rejected_for_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = self.make_service(directory)
            with self.assertRaisesRegex(
                service_module.KnowledgeBaseError,
                "only for PDF",
            ):
                service.read("index.md", 1, 2)


if __name__ == "__main__":
    unittest.main()
