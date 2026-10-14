---
id: "KB-KSS-02"
title: "Binomial line-length relation"
paper: "arXiv:2110.08973v3"
paper_slug: "kornerup-spooky-pebble-game"
evidence: "PAPER"
knowledge_type: "exact-result"
source_pages: "PDF pp. 3 and 10; Lemma 3.5; Theorem 3.6"
tags:
  - "spooky pebble game"
  - "ghosting"
  - "measurement record"
  - "time-space tradeoff"
  - "binomial bound"
  - "exact-result"
related:
  - "KB-KSS-01"
  - "KB-KSS-03"
---

# KB-KSS-02 — Binomial line-length relation

> Binomial relations characterize the line length reachable with a bounded number of pebbles and a time parameter.

The exact relation appears in two closely related forms:

- **Unghosting, Lemma 3.5:** if
  \[
  \boxed{n\leq\binom{m+s-1}{s-1}},
  \]
  a line of length \(n\) can be unghosted with at most \(s\) pebbles and \(O(mn)\) steps.

- **Pebbling, Theorem 3.6:** after the one-pebble conversion,
  \[
  \boxed{n\leq\binom{m+s-2}{s-2}+1},
  \]
  a line of length \(n\) can be pebbled with at most \(s\) pebbles and \(O(mn)\) steps.

The paper's summary table suppresses the harmless \(+1\) and presents the condition in the form \(\binom{m+s-2}{s-2}\geq n\). (pp. 3 and 10.)

## Transfer note

This node is source-grounded, but its reported resource result is valid only under the paper’s representation, map shape, workspace, and measurement assumptions. Use the linked concept pages before importing it into another arithmetic stack.

## Related nodes

- [KB-KSS-01 — Ghosting transformation and precondition](ghosting-transformation.md)
- [KB-KSS-03 — Memory that remains live](live-classical-memory.md)

## Source

- [Niels Kornerup, Jonathan Sadun, and David Soloveichik, “Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements,” arXiv:2110.08973v3.](../sources/2110.08973v3.md)
- Location: PDF pp. 3 and 10; Lemma 3.5; Theorem 3.6
