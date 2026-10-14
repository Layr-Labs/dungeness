from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = ROOT / "knowledge-bases/users/bx/ecdsa-8-raw-paper-kb-v1"
OUTPUT_DIR = Path("/tmp/ecdsa-8-paper-v2-text")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    manifest: list[dict[str, object]] = []
    for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
        reader = PdfReader(pdf_path)
        parts: list[str] = []
        page_words: list[int] = []
        for index, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").replace("\x00", "")
            page_words.append(len(text.split()))
            parts.append(f"\n\n===== SOURCE PAGE {index} =====\n\n{text.rstrip()}\n")

        output_path = OUTPUT_DIR / f"{pdf_path.stem}.txt"
        output_path.write_text("".join(parts), encoding="utf-8")
        manifest.append(
            {
                "source_pdf": pdf_path.name,
                "page_count": len(reader.pages),
                "text_path": output_path.name,
                "word_count": sum(page_words),
                "page_word_counts": page_words,
            }
        )

    (OUTPUT_DIR / "extraction-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
