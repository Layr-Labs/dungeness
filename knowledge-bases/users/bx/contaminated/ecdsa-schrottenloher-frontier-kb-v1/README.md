# Schrottenloher question-first research frontier

This knowledge base contains the same principal paper and benchmark adaptation
material as the existing single-paper KB, but it is organized in a deliberately
different way.

It has:

- no paper-section summaries;
- no catalog of isolated mechanism nodes;
- no attempt to present the paper as one implementation plan.

Instead, each retrieval unit is a **research dossier** centered on an unresolved
design question. A dossier places several facts, constraints, and possible
transformations together so that the solver can reason about changing the
architecture rather than merely reproducing it.

The intended progression is:

```text
build a valid paper-derived architecture
  -> identify the actual score owner
  -> select an unresolved dossier
  -> derive a transformation
  -> falsify it cheaply
  -> evaluate it
  -> revisit a different frontier
```

Evidence labels:

- **[PAPER]** is stated by arXiv:2606.02235v1.
- **[CODE]** comes from the paper's companion implementation.
- **[BENCHMARK]** comes from the local task or evaluator contract.
- **[INFERENCE]** is a proposed derivation or experiment, not an established result.

Begin with [`START.md`](START.md).
