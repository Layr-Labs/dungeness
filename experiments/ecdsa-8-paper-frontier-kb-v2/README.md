# ECDSA eight-paper frontier KB v2

This directory contains the reproducibility utilities used to build and
validate `knowledge-base:users/bx/contaminated/ecdsa-8-paper-frontier-kb-v2`.

## Utilities

- `build_source_layer.py` copies the eight source PDFs and creates
  page-delimited Markdown with a provenance manifest.
- `extract_sources.py` creates temporary whole-document text extractions under
  `/tmp/ecdsa-8-paper-v2-text`.
- `render_representative_pages.py` renders selected source pages for visual
  inspection under `/tmp/ecdsa-kb-v2-representative-pages`.
- `validate_kb_v2.py` validates the run-spec preload, document/page counts, and
  the retrieval query suite.

Run the utilities from the repository root.
