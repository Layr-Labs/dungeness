from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path
import re
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SPEC = (
    ROOT
    / "run-specs/users/bx/contaminated/"
    "ecdsa-astra-high-8-paper-frontier-v2-36usd/"
    "ecdsa-astra-high-8-paper-frontier-v2-36usd.yaml"
)


def load_module(name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


cli = load_module("dungeness_kb_v2_cli", ROOT / "dungeness")
build = load_module(
    "dungeness_kb_v2_build",
    ROOT / "adapters/harbor/build.py",
)
server = load_module(
    "dungeness_kb_v2_server",
    ROOT / "services/knowledge-base/server.py",
)


_, run_spec = cli.load_run_spec(str(SPEC))
cli.validate_run_spec_knowledge_base(run_spec)
configured = run_spec["initialization"]["knowledge_base"]
preload = build.resolve_knowledge_base_preload(configured)
assert preload is not None

assert preload["ref"] == "knowledge-base:users/bx/contaminated/ecdsa-8-paper-frontier-kb-v2"
assert len(preload["documents"]) == 8
assert sum(item["pages"] for item in preload["documents"]) == 227
assert len([name for name in preload["files"] if name.endswith(".pdf")]) == 8
assert len(
    [
        name
        for name in preload["files"]
        if name.startswith("source-pages/") and name.endswith(".md")
    ]
) == 227

with tempfile.TemporaryDirectory() as directory:
    service_root = Path(directory) / "knowledge-base"
    service_root.mkdir()
    resolved = build.materialize_knowledge_base_service(preload, service_root)
    content = service_root / "content"

    assert resolved["document_count"] == 8
    assert resolved["total_page_count"] == 227
    assert len(resolved["files"]) >= 265

    kb = server.KnowledgeBaseService(
        content,
        Path(directory) / "usage",
        "kb-v2-validation",
        behavior_feedback_config={"enabled": False, "mode": "off"},
    )
    assert len(kb.pages) >= 263

    suite = (
        content / "coverage/query-suite.md"
    ).read_text(encoding="utf-8")
    queries = re.findall(r"^\| `([^`]+)` \|", suite, flags=re.MULTILINE)
    assert len(queries) >= 50
    for query in queries:
        result = kb.search(query, max_results=10, context_lines=4)
        assert result["status"] == "matches", query
        assert result["results"], query
        assert any(
            item["source"] != "coverage/query-suite.md"
            for item in result["results"]
        ), query

print(
    "validated",
    {
        "selected_files": len(preload["files"]),
        "documents": len(preload["documents"]),
        "pdf_pages": sum(item["pages"] for item in preload["documents"]),
        "retrieval_queries": len(queries),
        "layers": preload["layers"],
    },
)
