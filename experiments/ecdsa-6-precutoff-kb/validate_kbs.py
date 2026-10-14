from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path
import re
import tempfile


ROOT = Path(__file__).resolve().parents[2]
RAW_SPEC = (
    ROOT
    / "run-specs/users/bx/ecdsa-astra-high-raw-6-precutoff-12usd/"
    "ecdsa-astra-high-raw-6-precutoff-12usd.yaml"
)
STRUCTURED_SPEC = (
    ROOT
    / "run-specs/users/bx/ecdsa-astra-high-structured-6-precutoff-12usd/"
    "ecdsa-astra-high-structured-6-precutoff-12usd.yaml"
)
STRUCTURED_ROOT = (
    ROOT / "knowledge-bases/users/bx/ecdsa-6-precutoff-mechanism-kb-v1"
)


def load_module(name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


cli = load_module("dungeness_six_kb_cli", ROOT / "dungeness")
build = load_module(
    "dungeness_six_kb_build",
    ROOT / "src/dungeness/compiler.py",
)
server = load_module(
    "dungeness_six_kb_server",
    ROOT / "services/knowledge-base/server.py",
)


def resolve(spec_path: Path) -> dict[str, object]:
    _, run_spec = cli.load_run_spec(str(spec_path))
    cli.validate_run_spec_knowledge_base(run_spec)
    configured = run_spec["initialization"]["knowledge_base"]
    preload = build.resolve_knowledge_base_preload(configured)
    assert preload is not None
    return preload


raw = resolve(RAW_SPEC)
structured = resolve(STRUCTURED_SPEC)

for preload in (raw, structured):
    assert len(preload["documents"]) == 6
    assert sum(item["pages"] for item in preload["documents"]) == 158
    assert len([name for name in preload["files"] if name.endswith(".pdf")]) == 6

source_pages = [
    name
    for name in structured["files"]
    if name.startswith("source-pages/") and name.endswith(".md")
]
assert len(source_pages) == 158

for path in STRUCTURED_ROOT.rglob("*"):
    if path.suffix.lower() not in {".md", ".yaml", ".yml", ".txt"}:
        continue
    text = path.read_text(encoding="utf-8")
    for forbidden in (
        r"\bSchrottenloher\b",
        r"2606\.02235",
        r"2607\.13816",
        r"\bLuo et al\b",
    ):
        assert re.search(forbidden, text, flags=re.IGNORECASE) is None, (
            path,
            forbidden,
        )

with tempfile.TemporaryDirectory() as directory:
    service_root = Path(directory) / "knowledge-base"
    service_root.mkdir()
    resolved = build.materialize_knowledge_base_service(
        structured,
        service_root,
    )
    content = service_root / "content"

    assert resolved["document_count"] == 6
    assert resolved["total_page_count"] == 158
    assert len(resolved["files"]) >= 180

    kb = server.KnowledgeBaseService(
        content,
        Path(directory) / "usage",
        "six-kb-validation",
        behavior_feedback_config={"enabled": False, "mode": "off"},
    )
    assert len(kb.pages) >= 178

    suite = (content / "coverage/query-suite.md").read_text(encoding="utf-8")
    queries = re.findall(r"^\| `([^`]+)` \|", suite, flags=re.MULTILINE)
    assert len(queries) == 10
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
        "raw_files": len(raw["files"]),
        "structured_files": len(structured["files"]),
        "documents": len(structured["documents"]),
        "pdf_pages": sum(item["pages"] for item in structured["documents"]),
        "source_pages": len(source_pages),
        "retrieval_queries": len(queries),
        "layers": structured["layers"],
    },
)
