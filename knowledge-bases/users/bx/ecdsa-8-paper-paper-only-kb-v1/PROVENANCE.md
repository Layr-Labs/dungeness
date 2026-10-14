# Provenance boundary

## Permitted inputs

The complete information boundary is exactly these artifacts:

| Source | PDF pages | SHA-256 |
|---|---:|---|
| arXiv:2606.02235v1 | 19 | `8744ef6db6c60b62d952a1dd24e5bd433242af970f4755c8b49b020a731584af` |
| arXiv:2410.00899v1 | 6 | `5da56cc0dd20b0afe73b3d0a188ba7e0e9826960c37b9b972671520755a74713` |
| arXiv:2407.20167v1 | 45 | `c5b152e5dbfdbc767e49edaec45f3550e623fdefa269fdabed0ab578d7a392f0` |
| arXiv:2507.23079v1 | 8 | `31c8fb8d52329c79cd29816d8c22087d5e84aa6fee46458f1f5c0ef726adba3f` |
| arXiv:2110.08973v3 | 25 | `13ee62c1108a9a2bd9654235f6ad6cffe30660c35f524b60dd54a38af8d18997` |
| arXiv:2607.13816v2 | 50 | `8e61e2ce2be1a9a9404c67fe2b42b1e381093e215ada2e20ce3f2de925938901` |
| arXiv:2510.10967v1 | 52 | `dcbbd0034ebcc3918a31ecc211ab108ec3a11d02840a78f504f915b73a5370ca` |
| IACR ePrint 2020/077 | 22 | `ed7daaba41f3a6d2a42536b977a91a97e343a23a9f0d9324d3b9aaf3eb0848c2` |

Total: 8 papers and 227 PDF pages.

## Derived material

The Markdown under `source-pages/` is page-delimited text extraction from the
PDFs. The files under `paper-cards/` paraphrase only those source pages and
link back to them. `mechanism-map.md` reorganizes claims already present in
the paper cards.

## Excluded inputs

No codebase, auxiliary software, solution artifact, result record, external
note, or undocumented observation is part of this edition. No application
configuration or prior outcome is used to rank the mechanisms.

The machine-checkable artifact manifest is
[`source-pages/source-page-manifest.json`](source-pages/source-page-manifest.json).
