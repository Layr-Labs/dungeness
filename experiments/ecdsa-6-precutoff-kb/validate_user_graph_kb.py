from __future__ import annotations

import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SPEC = (
    ROOT
    / "run-specs/users/bx/ecdsa-astra-high-user-graph-6-precutoff-12usd/"
    "ecdsa-astra-high-user-graph-6-precutoff-12usd.yaml"
)


def load_module(name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


cli = load_module("dungeness_user_graph_cli", ROOT / "dungeness")
build = load_module(
    "dungeness_user_graph_build",
    ROOT / "src/dungeness/compiler.py",
)
server = load_module(
    "dungeness_user_graph_server",
    ROOT / "services/knowledge-base/server.py",
)

_, run_spec = cli.load_run_spec(str(SPEC))
cli.validate_run_spec_knowledge_base(run_spec)
configured = run_spec["initialization"]["knowledge_base"]
preload = build.resolve_knowledge_base_preload(configured)
assert preload is not None

assert preload["ref"] == (
    "knowledge-base:users/bx/ecdsa-6-precutoff-user-graph-kb-v1"
)
assert preload["documents"] == []
assert len(preload["files"]) == 49
assert len(
    [name for name in preload["files"] if name.startswith("nodes/")]
) == 18
assert len(
    [name for name in preload["files"] if name.startswith("concepts/")]
) == 8

queries = (
    "controlled add subtract prime field interface",
    "measurement cleanup comparison flag expected Toffoli",
    "carry venting dirty ancilla classical offset",
    "ghosting classical memory phase obligation",
    "implicit Bezout direct division Dialog replay",
    "Kaliski fixed rounds pseudo inverse correction",
    "producer consumer workspace reuse multiplication",
)

with tempfile.TemporaryDirectory() as directory:
    service_root = Path(directory) / "knowledge-base"
    service_root.mkdir()
    resolved = build.materialize_knowledge_base_service(
        preload,
        service_root,
    )
    content = service_root / "content"
    assert resolved["document_count"] == 0
    assert len(resolved["files"]) >= 49

    kb = server.KnowledgeBaseService(
        content,
        Path(directory) / "usage",
        "user-graph-kb-validation",
        behavior_feedback_config={"enabled": False, "mode": "off"},
    )
    for query in queries:
        result = kb.search(query, max_results=10, context_lines=4)
        assert result["status"] == "matches", query
        assert result["results"], query
        assert any(
            item["source"].startswith(("nodes/", "concepts/", "sections/"))
            for item in result["results"]
        ), query

print(
    "validated",
    {
        "selected_files": len(preload["files"]),
        "documents": len(preload["documents"]),
        "atomic_nodes": 18,
        "concept_pages": 8,
        "retrieval_queries": len(queries),
        "layers": preload["layers"],
    },
)
