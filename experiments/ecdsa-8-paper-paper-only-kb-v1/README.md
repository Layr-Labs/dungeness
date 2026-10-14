# Paper-only KB validation

`validate_paper_only.py` verifies that:

- all eight PDFs have the expected hashes and page counts;
- all 227 searchable page files can be regenerated exactly from those PDFs;
- the authored layer contains none of the disallowed external-solution terms,
  identifiers, values, labels, paths, or URLs;
- the structured layer contains 29 sections, 80 atomic nodes, and 20 concepts;
- every authored link resolves inside the knowledge base;
- all eight paper cards contain multiple direct evidence citations.

Run from the repository root:

```text
UV_CACHE_DIR=/tmp/dungeness-paper-only-uv-cache \
uv run --with pypdf==6.0.0 --with PyYAML==6.0.3 \
python experiments/ecdsa-8-paper-paper-only-kb-v1/validate_paper_only.py
```
