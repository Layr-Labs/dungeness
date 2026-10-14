---
kind: research-dossier
id: field-representation-and-reduction
depends_on: [arithmetic-control-structure]
---

# Dossier: choose the residue regime at phase boundaries

Field arithmetic cost depends on three distinct choices:

```text
residue representation
allowed intermediate range
time and method of canonical reduction
```

## Paper regimes

### secp256k1 pseudo-Mersenne folding

**[PAPER: Schrottenloher]**

```text
p = 2^256 - f
f = 2^32 + 977
2^256 == f mod p
```

Overflow can be folded by a low-width addition of `f`. The fast controlled
addition does not by itself canonicalize the exceptional relation `x+y=p`.
The companion construction therefore distinguishes an exact early regime from
a cheaper bulk regime and uses bounded carry/comparison windows.

### Montgomery arithmetic

**[PAPER: Litinski and Häner]** Montgomery representation supports generic
prime modular multiplication, windowing, and add-and-halve reduction.
Litinski's multiplier gains depend on controlled add-subtract and global
corrections; Häner integrates Montgomery arithmetic into a complete ECDLP
stack.

Montgomery counts are not directly comparable to a pseudo-Mersenne replay cell.
Entering and leaving the representation, output placement, and cleanup must be
included.

### Explicit generic-prime state

**[PAPER: Luo]** The low-space EEA and point-add architecture operates over
prime fields with explicit shared work registers. Its main gain is width, while
the literal arithmetic has a much larger reported Toffoli count.

## Research frontier

**[INFERENCE]** Do not ask only “pseudo-Mersenne or Montgomery?” Ask:

- Which replay symbols can tolerate a redundant residue interval?
- Which steps can postpone canonicalization until a later consumer?
- Can a Litinski-style global correction coincide with a required fold?
- Can a Gidney constant adder implement only the fold or normalization path?
- Which early or terminal states can equal exactly `p`?
- Can different phases use different representations without paying repeated
  conversions?

## State the range invariant

For every proposed fused cell, prove:

```text
input interval
integer expression before reduction
number and location of overflow bits
output interval
condition for equality with p
condition for a carry escaping a truncated window
relation used to erase each flag
```

Approximate windows require a benchmark-compatible failure argument; a random
paper test is not enough.

## Decisive experiment

Use exhaustive small moduli with the same structural form `2^n-f`. Compare:

```text
canonicalize every operation
fold every operation but canonicalize at phase boundary
symbol-specific fold/correction cells
one redundant interval across several replay steps
```

Include inverse and phase tests. Promote only candidates whose proven range
invariant survives the complete benchmark, especially equality-to-modulus and
long-carry cases.
