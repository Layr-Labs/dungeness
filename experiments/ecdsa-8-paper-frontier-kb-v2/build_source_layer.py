from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = ROOT / "knowledge-bases/users/bx/ecdsa-8-raw-paper-kb-v1"
TARGET = ROOT / "knowledge-bases/users/bx/contaminated/ecdsa-8-paper-frontier-kb-v2"

SOURCES = {
    "2020-077": {
        "slug": "haner-2020-077",
        "source_id": "IACR ePrint 2020/077",
        "title": "Improved quantum circuits for elliptic curve discrete logarithms",
    },
    "2110.08973v3": {
        "slug": "spooky-2110.08973v3",
        "source_id": "arXiv:2110.08973v3",
        "title": "Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements",
    },
    "2407.20167v1": {
        "slug": "luongo-2407.20167v1",
        "source_id": "arXiv:2407.20167v1",
        "title": "Measurement-based uncomputation of quantum circuits for modular arithmetic",
    },
    "2410.00899v1": {
        "slug": "litinski-2410.00899v1",
        "source_id": "arXiv:2410.00899v1",
        "title": "Quantum schoolbook multiplication with fewer Toffoli gates",
    },
    "2507.23079v1": {
        "slug": "gidney-2507.23079v1",
        "source_id": "arXiv:2507.23079v1",
        "title": "A Classical-Quantum Adder with Constant Workspace and Linear Gates",
    },
    "2510.10967v1": {
        "slug": "khattar-2510.10967v1",
        "source_id": "arXiv:2510.10967v1",
        "title": "Verifiable Quantum Advantage via Optimized DQI Circuits",
    },
    "2606.02235v1": {
        "slug": "schrottenloher-2606.02235v1",
        "source_id": "arXiv:2606.02235v1",
        "title": "Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms",
    },
    "2607.13816v2": {
        "slug": "luo-2607.13816v2",
        "source_id": "arXiv:2607.13816v2",
        "title": "Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition",
    },
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


def main() -> None:
    raw_dir = TARGET / "raw"
    page_root = TARGET / "source-pages"
    raw_dir.mkdir(parents=True, exist_ok=True)
    page_root.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, object]] = []
    for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
        metadata = SOURCES[pdf_path.stem]
        copied_pdf = raw_dir / pdf_path.name
        shutil.copy2(pdf_path, copied_pdf)

        reader = PdfReader(pdf_path)
        source_dir = page_root / str(metadata["slug"])
        source_dir.mkdir(parents=True, exist_ok=True)
        page_records: list[dict[str, object]] = []

        width = max(2, len(str(len(reader.pages))))
        for page_number, page in enumerate(reader.pages, start=1):
            text = clean_text(page.extract_text() or "")
            relative_path = (
                Path("source-pages")
                / str(metadata["slug"])
                / f"page-{page_number:0{width}d}.md"
            )
            page_path = TARGET / relative_path
            page_path.write_text(
                "\n".join(
                    [
                        "---",
                        "kind: source-page",
                        f"source_id: {metadata['source_id']}",
                        f"source_pdf: raw/{pdf_path.name}",
                        f"source_page: {page_number}",
                        "---",
                        "",
                        f"# {metadata['title']} - source page {page_number}",
                        "",
                        "The text below is a page-delimited extraction of the unchanged source PDF.",
                        "",
                        text,
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            page_records.append(
                {
                    "page": page_number,
                    "path": relative_path.as_posix(),
                    "word_count": len(text.split()),
                }
            )

        manifest.append(
            {
                **metadata,
                "pdf": f"raw/{pdf_path.name}",
                "sha256": sha256(pdf_path),
                "page_count": len(reader.pages),
                "word_count": sum(int(page["word_count"]) for page in page_records),
                "pages": page_records,
            }
        )

    manifest_path = TARGET / "source-pages/source-page-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
