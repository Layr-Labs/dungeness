from __future__ import annotations

from contextlib import redirect_stdout
from contextlib import redirect_stderr
import importlib.util
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


client = load_module(
    "knowledge_base_client",
    REPOSITORY_ROOT / "agents/common/knowledge_base.py",
)
hook = load_module(
    "knowledge_base_hook",
    REPOSITORY_ROOT / "agents/common/research_state_hook.py",
)


class FakeResponse:
    def __init__(self, document):
        self.document = document

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.document).encode("utf-8")


class KnowledgeBaseToolTests(unittest.TestCase):
    def test_read_prints_complete_sidecar_content(self) -> None:
        page = "# Point Addition\n\nReduce live width.\n"
        with patch.object(
            client.urllib.request,
            "urlopen",
            return_value=FakeResponse(
                {"page": "nodes/point.md", "content": page}
            ),
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                client.main(["read", "nodes/point.md"])
        self.assertEqual(output.getvalue(), page)

    def test_read_only_interface_exposes_only_read_command(self) -> None:
        with patch.dict(
            os.environ,
            {"DUNGENESS_KNOWLEDGE_BASE_OPERATIONS": "read"},
        ):
            parser = client.build_parser()
            choices = parser._subparsers._group_actions[0].choices
            self.assertEqual(set(choices), {"read"})
            with redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    parser.parse_args(["search", "point"])

    def test_pdf_page_window_is_sent_to_read_endpoint(self) -> None:
        with patch.object(
            client.urllib.request,
            "urlopen",
            return_value=FakeResponse({"content": "pages 1-5\n"}),
        ) as urlopen:
            output = io.StringIO()
            with redirect_stdout(output):
                client.main([
                    "read",
                    "paper.pdf",
                    "--pages",
                    "1-5",
                ])
        request = urlopen.call_args.args[0]
        self.assertEqual(
            json.loads(request.data),
            {
                "page": "paper.pdf",
                "first_page": 1,
                "last_page": 5,
            },
        )
        self.assertEqual(output.getvalue(), "pages 1-5\n")

    def test_search_uses_sidecar_endpoint(self) -> None:
        with patch.object(
            client.urllib.request,
            "urlopen",
            return_value=FakeResponse({"results": []}),
        ) as urlopen:
            output = io.StringIO()
            with redirect_stdout(output):
                client.main(["search", "inversion", "ancilla"])
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "http://knowledge-base:8078/v1/search",
        )
        self.assertEqual(
            json.loads(request.data),
            {
                "query": "inversion ancilla",
                "max_results": 8,
                "context_lines": 3,
            },
        )

    def test_inspire_submits_exact_passage_and_candidate_change(self) -> None:
        with patch.object(
            client.urllib.request,
            "urlopen",
            return_value=FakeResponse(
                {
                    "qualifying": True,
                    "kb_lookup_id": "kb-lookup:1",
                }
            ),
        ) as urlopen:
            output = io.StringIO()
            with redirect_stdout(output):
                client.main([
                    "inspire",
                    "--search-id",
                    "kb-search:1",
                    "--passage",
                    "nodes/inversion.md:L10-L18",
                    "--takeaway",
                    "Reuse the released state register.",
                    "--planned-change",
                    "Alias it during multiplication.",
                ])
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "http://knowledge-base:8078/v1/inspire",
        )
        self.assertEqual(
            json.loads(request.data),
            {
                "search_id": "kb-search:1",
                "passages": [{
                    "source": "nodes/inversion.md",
                    "line_start": 10,
                    "line_end": 18,
                }],
                "takeaway": "Reuse the released state register.",
                "planned_change": "Alias it during multiplication.",
            },
        )

    def hook_input(self, command: str) -> dict:
        return {
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }

    def test_hook_allows_direct_knowledge_base_command(self) -> None:
        with patch.dict(
            os.environ,
            {"DUNGENESS_KNOWLEDGE_BASE_URL": "http://knowledge-base:8078"},
        ):
            self.assertEqual(
                hook.pre_tool_use(
                    self.hook_input(
                        'knowledge-base search "inversion|ancilla|width"'
                    )
                ),
                {},
            )

    def test_hook_denies_hidden_or_compound_knowledge_base_command(self) -> None:
        with patch.dict(
            os.environ,
            {"DUNGENESS_KNOWLEDGE_BASE_URL": "http://knowledge-base:8078"},
        ):
            for command in [
                "knowledge-base read README.md >/dev/null",
                "knowledge-base read README.md | head",
                "cd /workspace/repo && knowledge-base read README.md",
                "knowledge-base read README.md; true",
            ]:
                with self.subTest(command=command):
                    decision = hook.pre_tool_use(self.hook_input(command))
                    self.assertEqual(
                        decision["hookSpecificOutput"]["permissionDecision"],
                        "deny",
                    )

    def test_hook_ignores_literal_knowledge_base_arguments(self) -> None:
        with patch.dict(
            os.environ,
            {"DUNGENESS_KNOWLEDGE_BASE_URL": "http://knowledge-base:8078"},
        ):
            self.assertEqual(
                hook.pre_tool_use(
                    self.hook_input("rg -n knowledge-base README.md")
                ),
                {},
            )


if __name__ == "__main__":
    unittest.main()
