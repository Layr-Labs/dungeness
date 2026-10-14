# ECDSA eight-paper evidence-preserving research frontier

This knowledge base is designed to test whether preprocessing helps an agent
continue research beyond the conclusion of a paper without starving it of the
paper's details.

It deliberately contains four distinct layers:

1. **Orientation** tells the agent how to enter the problem and how to reopen
   the design after obtaining a valid baseline.
2. **Decision dossiers** organize the papers by architectural question rather
   than by publication.
3. **Operational evidence cards** preserve algorithms, state invariants,
   resource formulas, cleanup protocols, assumptions, and transfer barriers
   paper by paper.
4. **Source evidence** contains a searchable Markdown file for every one of the
   227 PDF pages, plus unchanged copies of all eight PDFs.

The page extraction contains about 104,000 source words before the curated
layers are counted. A synthesis statement is therefore a navigation aid, not a
replacement for source evidence.

## Why this differs from the thin frontier KB

The earlier frontier KB compressed eight papers into a small set of dossiers.
Its manifest named an upstream atomic KB, but that relationship did not make
the upstream files searchable inside a run. This version is self-contained.

The important experimental contrast is:

```text
thin synthesis
    versus
evidence-preserving transformation
    = decision structure + operational detail + complete page fallback
```

This version also avoids importing discoveries from previous Astra runs. It
should supply published mechanisms and useful research coordinates while
leaving the benchmark agent responsible for new compositions and measurements.

## Evidence discipline

- `[EVIDENCE]` means the statement is paraphrased from the linked paper pages.
- `[INFERENCE]` means the statement is a proposed interpretation, bridge, or
  experiment rather than a result established by a paper.
- A paper's local cost model is not silently converted into the benchmark's
  `average Toffoli × maximum referenced qubit ID` objective.
- A mechanism is not called compatible merely because two papers use the same
  noun. Register layout, representation, controls, cleanup, and reverse
  behavior are part of its interface.

The extraction manifest, page counts, word counts, and PDF hashes are recorded
in [`source-pages/source-page-manifest.json`](source-pages/source-page-manifest.json).
