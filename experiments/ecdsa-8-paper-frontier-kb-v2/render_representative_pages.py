from __future__ import annotations

from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[2]
KB = ROOT / "knowledge-bases/users/bx/contaminated/ecdsa-8-paper-frontier-kb-v2/raw"
OUT = Path("/tmp/ecdsa-kb-v2-representative-pages")

PAGES = {
    "schrottenloher-p10": ("2606.02235v1.pdf", 10),
    "litinski-p2": ("2410.00899v1.pdf", 2),
    "luongo-p35": ("2407.20167v1.pdf", 35),
    "gidney-p7": ("2507.23079v1.pdf", 7),
    "spooky-p5": ("2110.08973v3.pdf", 5),
    "luo-p30": ("2607.13816v2.pdf", 30),
    "khattar-p11": ("2510.10967v1.pdf", 11),
    "haner-p9": ("2020-077.pdf", 9),
}


OUT.mkdir(parents=True, exist_ok=True)
for name, (pdf_name, one_based_page) in PAGES.items():
    document = fitz.open(KB / pdf_name)
    page = document[one_based_page - 1]
    pixmap = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
    target = OUT / f"{name}.png"
    pixmap.save(target)
    print(target)
