from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import re
import tempfile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
KB = ROOT / "knowledge-bases/users/bx/ecdsa-8-paper-paper-only-kb-v1"

EXPECTED = {
    "2020-077.pdf": {
        "slug": "haner-2020-077",
        "source_id": "IACR ePrint 2020/077",
        "title": "Improved quantum circuits for elliptic curve discrete logarithms",
        "pages": 22,
        "sha256": "ed7daaba41f3a6d2a42536b977a91a97e343a23a9f0d9324d3b9aaf3eb0848c2",
    },
    "2110.08973v3.pdf": {
        "slug": "spooky-2110.08973v3",
        "source_id": "arXiv:2110.08973v3",
        "title": "Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements",
        "pages": 25,
        "sha256": "13ee62c1108a9a2bd9654235f6ad6cffe30660c35f524b60dd54a38af8d18997",
    },
    "2407.20167v1.pdf": {
        "slug": "luongo-2407.20167v1",
        "source_id": "arXiv:2407.20167v1",
        "title": "Measurement-based uncomputation of quantum circuits for modular arithmetic",
        "pages": 45,
        "sha256": "c5b152e5dbfdbc767e49edaec45f3550e623fdefa269fdabed0ab578d7a392f0",
    },
    "2410.00899v1.pdf": {
        "slug": "litinski-2410.00899v1",
        "source_id": "arXiv:2410.00899v1",
        "title": "Quantum schoolbook multiplication with fewer Toffoli gates",
        "pages": 6,
        "sha256": "5da56cc0dd20b0afe73b3d0a188ba7e0e9826960c37b9b972671520755a74713",
    },
    "2507.23079v1.pdf": {
        "slug": "gidney-2507.23079v1",
        "source_id": "arXiv:2507.23079v1",
        "title": "A Classical-Quantum Adder with Constant Workspace and Linear Gates",
        "pages": 8,
        "sha256": "31c8fb8d52329c79cd29816d8c22087d5e84aa6fee46458f1f5c0ef726adba3f",
    },
    "2510.10967v1.pdf": {
        "slug": "khattar-2510.10967v1",
        "source_id": "arXiv:2510.10967v1",
        "title": "Verifiable Quantum Advantage via Optimized DQI Circuits",
        "pages": 52,
        "sha256": "dcbbd0034ebcc3918a31ecc211ab108ec3a11d02840a78f504f915b73a5370ca",
    },
    "2606.02235v1.pdf": {
        "slug": "schrottenloher-2606.02235v1",
        "source_id": "arXiv:2606.02235v1",
        "title": "Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms",
        "pages": 19,
        "sha256": "8744ef6db6c60b62d952a1dd24e5bd433242af970f4755c8b49b020a731584af",
    },
    "2607.13816v2.pdf": {
        "slug": "luo-2607.13816v2",
        "source_id": "arXiv:2607.13816v2",
        "title": "Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition",
        "pages": 50,
        "sha256": "8e61e2ce2be1a9a9404c67fe2b42b1e381093e215ada2e20ce3f2de925938901",
    },
}

FORBIDDEN_CURATED_PATTERNS = {
    "challenge name": r"ecdsa\.fail",
    "challenge terminology": r"\bbenchmark\b|\bleaderboard\b|\bsubmission\b",
    "prior execution evidence": r"\btrusted run\b|\blocal run\b|\bAstra\b|\bHarbor\b",
    "live solution state": (
        r"\blive architecture\b|\bcurrent implementation\b|"
        r"\bcurrent source\b|\balready (?:tried|measured|implemented)\b"
    ),
    "software supplements": r"\bcompanion\b|\brepository\b",
    "solution symbols": r"pingpong|ping-pong|build_pingpong|pingpong_div|src/|\.rs\b",
    "known leaked commit": r"c1adf3e",
    "known leaked values": (
        r"1,207,540,991|1,177,751,124|1,137,423,406|10,704,574,395|"
        r"944,129\.342|921,558"
    ),
    "known experiment outcomes": (
        r"saved 21 qubits|about 4\.2k|generic Bennett|radix-4|Karatsuba-2"
    ),
    "software-only tuning parameters": (
        r"(?-i:ITER_CAN_BE_Q|ITERATIONS_VAR|PADDING2?|TRUNCATE)|"
        r"\b402\b|\b670\b|\b37 bits\b"
    ),
    "removed mixed-provenance pages": (
        r"benchmark-adaptation|spooky-pingpong|implementation-parameters|"
        r"current-benchmark-architecture|porting-to-ecdsa"
    ),
    "disallowed labels": r"\[CODE\]|\[BENCHMARK\]|\[INFERENCE\]",
    "application metric": r"\bscore\b",
    "external URL": r"https?://",
    "absolute path": r"/Users/",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_text(text: str) -> str:
    normalized = (
        text.replace("\x00", "")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("](", "]\\(")
    )
    return "\n".join(line.rstrip() for line in normalized.splitlines()).rstrip()


def expected_page(
    *,
    source_id: str,
    source_pdf: str,
    title: str,
    page_number: int,
    text: str,
) -> str:
    return "\n".join(
        [
            "---",
            "kind: source-page",
            f"source_id: {source_id}",
            f"source_pdf: raw/{source_pdf}",
            f"source_page: {page_number}",
            "---",
            "",
            f"# {title} - source page {page_number}",
            "",
            "The text below is a page-delimited extraction of the unchanged source PDF.",
            "",
            clean_text(text),
            "",
        ]
    )


def curated_files() -> list[Path]:
    files: list[Path] = []
    for path in KB.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(KB)
        if relative.parts[0] in {"raw", "source-pages"}:
            continue
        files.append(path)
    return sorted(files)


def load_module(name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def check_links(paths: list[Path]) -> int:
    count = 0
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in paths:
        if path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for match in link_pattern.finditer(text):
            destination = match.group(1).split("#", 1)[0]
            assert not re.match(r"^[a-z]+://", destination), (path, destination)
            resolved = (path.parent / destination).resolve()
            assert resolved == KB.resolve() or KB.resolve() in resolved.parents, (
                path,
                destination,
            )
            assert resolved.exists(), (path, destination)
            count += 1
    return count


def main() -> None:
    assert KB.is_dir()

    pdfs = sorted((KB / "raw").glob("*.pdf"))
    assert {path.name for path in pdfs} == set(EXPECTED)

    manifest = json.loads(
        (KB / "source-pages/source-page-manifest.json").read_text(encoding="utf-8")
    )
    assert len(manifest) == 8
    manifest_by_pdf = {Path(item["pdf"]).name: item for item in manifest}
    assert set(manifest_by_pdf) == set(EXPECTED)

    page_count = 0
    extracted_word_count = 0
    for pdf_path in pdfs:
        metadata = EXPECTED[pdf_path.name]
        record = manifest_by_pdf[pdf_path.name]
        assert sha256(pdf_path) == metadata["sha256"]
        assert record["sha256"] == metadata["sha256"]
        assert record["source_id"] == metadata["source_id"]
        assert record["title"] == metadata["title"]

        reader = PdfReader(pdf_path)
        assert len(reader.pages) == metadata["pages"]
        assert record["page_count"] == metadata["pages"]

        width = max(2, len(str(len(reader.pages))))
        for page_number, page in enumerate(reader.pages, start=1):
            page_path = (
                KB
                / "source-pages"
                / metadata["slug"]
                / f"page-{page_number:0{width}d}.md"
            )
            assert page_path.is_file(), page_path
            extracted = clean_text(page.extract_text() or "")
            assert page_path.read_text(encoding="utf-8") == expected_page(
                source_id=metadata["source_id"],
                source_pdf=pdf_path.name,
                title=metadata["title"],
                page_number=page_number,
                text=extracted,
            )
            page_count += 1
            extracted_word_count += len(extracted.split())

    assert page_count == 227
    assert extracted_word_count == 104166
    assert len(list((KB / "source-pages").glob("*/page-*.md"))) == 227

    authored = curated_files()
    authored_text = "\n".join(
        path.read_text(encoding="utf-8", errors="strict")
        for path in authored
        if path.suffix in {".md", ".yaml"}
    )
    for label, pattern in FORBIDDEN_CURATED_PATTERNS.items():
        match = re.search(pattern, authored_text, flags=re.IGNORECASE)
        assert match is None, (label, match.group(0) if match else None)

    cards = sorted((KB / "paper-cards").glob("*.md"))
    assert len(cards) == 8
    for card in cards:
        text = card.read_text(encoding="utf-8")
        assert text.count("**[EVIDENCE]**") >= 4, card
        assert text.count("../source-pages/") >= 4, card

    mechanism_map = (KB / "mechanism-map.md").read_text(encoding="utf-8")
    assert mechanism_map.count("**[SYNTHESIS]**") >= 4

    sections = sorted((KB / "sections").glob("*.md"))
    nodes = sorted((KB / "nodes").glob("*.md"))
    concepts = sorted((KB / "concepts").glob("*.md"))
    assert len(sections) == 29
    assert len(nodes) == 80
    assert len(concepts) == 20

    link_count = check_links(authored)
    assert link_count >= 250

    compiler = load_module(
        "dungeness_paper_only_compiler",
        ROOT / "adapters/harbor/build.py",
    )
    preload = compiler.resolve_knowledge_base_preload(
        {
            "ref": "knowledge-base:users/bx/ecdsa-8-paper-paper-only-kb-v1",
            "access": "sidecar",
        }
    )
    assert preload is not None
    assert preload["ref"] == (
        "knowledge-base:users/bx/ecdsa-8-paper-paper-only-kb-v1"
    )
    assert len(preload["documents"]) == 8
    assert sum(item["pages"] for item in preload["documents"]) == 227
    assert len(preload["files"]) == 385

    with tempfile.TemporaryDirectory() as directory:
        service_root = Path(directory) / "knowledge-base"
        service_root.mkdir()
        resolved = compiler.materialize_knowledge_base_service(
            preload,
            service_root,
        )
        assert resolved["document_count"] == 8
        assert resolved["total_page_count"] == 227
        # The materialized sidecar adds its injected manifest and metadata.
        assert len(resolved["files"]) == 387

    print(
        "validated",
        {
            "papers": len(pdfs),
            "pdf_pages": page_count,
            "extracted_words": extracted_word_count,
            "paper_cards": len(cards),
            "sections": len(sections),
            "nodes": len(nodes),
            "concepts": len(concepts),
            "curated_files": len(authored),
            "resolved_links": link_count,
            "preloaded_files": len(preload["files"]),
            "forbidden_pattern_hits": 0,
        },
    )


if __name__ == "__main__":
    main()
