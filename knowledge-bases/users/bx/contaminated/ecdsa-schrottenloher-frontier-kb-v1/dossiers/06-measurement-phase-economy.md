---
kind: research-dossier
id: measurement-phase-economy
depends_on: [replay-linear-compiler, reduction-regimes]
---

# Dossier: pay for information or pay for its phase

## Paper mechanism

**[PAPER]** A Boolean garbage bit can be measured in the X basis. One outcome
needs no expensive uncomputation; the other requires a phase correction based
on the original Boolean function.

Conceptually:

```text
compute g(x) into one qubit
use g
X-basis measure g
if outcome requires it:
    apply phase (-1)^g(x)
release the qubit
```

The saving is expected cost, not automatic deletion.

## Candidate objects

- temporary ANDs in a carry ladder;
- comparator outputs;
- overflow/fold flags;
- block-compression predicates;
- a complete obsolete register only if its value is cheaply reconstructible.

## Scale law

The larger the measured object, the more expensive its phase predicate can
become. A one-bit success does not imply that a field register is economical to
erase.

## Required implementation discipline

1. Retain the classical measurement outcome.
2. Define an explicit inverse protocol; mechanical gate-list reversal is not
   sufficient.
3. Test superpositions or the benchmark's phase checks.
4. Remove one phase correction and require the test to fail.
5. Compare average executed gates, not only emitted gates.
6. Confirm that released wires lower the hard maximum ID where it matters.

## Deeper question

**[INFERENCE]** Primitive boundaries affect phase-repair cost. If a comparison
or carry predicate is fused with the next replay cell, the same surviving
values may expose a cheaper phase oracle than the standalone primitive.

Test measurement only after deriving the predicate from the final fused cell,
not necessarily from the paper's original decomposition.
