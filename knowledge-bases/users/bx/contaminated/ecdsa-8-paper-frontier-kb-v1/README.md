# ECDSA eight-paper decision frontier

This knowledge base uses the same eight-paper evidence corpus as
`ecdsa-8-paper-kb-v1`, but changes the unit of retrieval.

The earlier KB decomposes papers into section notes, atomic mechanisms, and
concept summaries. This KB instead contains **decision dossiers**. Each dossier
puts several papers in tension around one unresolved architectural choice:

```text
Where should reversible information live?
Which recurrence should generate it?
Which arithmetic contract occurs at the hot loop?
When should a value be retained, recomputed, or measured?
Which cross-paper combinations are actually compatible?
```

A dossier is not a menu of paper claims. It includes:

- competing representations or mechanisms;
- the invariant they must all preserve;
- transfer barriers between them;
- bridge hypotheses that are not yet established;
- the smallest experiment capable of rejecting a hypothesis.

The KB deliberately has two operating phases:

```text
bootstrap: obtain or preserve a valid baseline quickly
frontier:  profile it, choose one unresolved decision, and test a bridge
```

This prevents the eight-paper corpus from becoming an expensive literature
survey before any executable candidate exists.

Evidence labels:

- **[PAPER]** is a claim or construction in one of the eight papers.
- **[CODE]** is a concrete choice in a pinned companion implementation.
- **[BENCHMARK]** is part of the static task or evaluator contract.
- **[INFERENCE]** is a proposed derivation, composition, or experiment.

Later Astra discoveries, locally tuned parameters, and trusted-run outcomes are
deliberately absent. The purpose is to test whether the organization itself can
help an agent derive work beyond any single paper.

Begin with [`START.md`](START.md).
