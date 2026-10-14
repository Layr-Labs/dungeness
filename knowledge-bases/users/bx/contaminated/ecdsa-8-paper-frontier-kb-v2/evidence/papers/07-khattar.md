# Khattar et al.: Dialog as a linear transition representation

Source: arXiv:2510.10967v1, *Verifiable Quantum Advantage via Optimized DQI
Circuits*.

## Operational role

Only part of this broad paper is relevant here: its reversible extended
Euclidean constructions over polynomial fields and the distinction between
explicit and implicit Bézout access.

The Dialog concept is valuable because it asks what downstream computation
actually needs. If a consumer only needs to apply the accumulated EEA
transformation, materializing a full inverse may be wasteful.

## Transition-matrix view

**[EVIDENCE]** Each EEA step is represented by a small invertible `2×2`
transition matrix. The product maps the input pair to `(gcd,0)` and contains
the Bézout transformation. See
[page 8](../../source-pages/khattar-2510.10967v1/page-08.md).

The paper separates:

- **explicit access**: compute and store the complete Bézout coefficients;
- **implicit access**: store a sequence of simple transition descriptions and
  apply them to a different vector when the result is needed.

See [page 9](../../source-pages/khattar-2510.10967v1/page-09.md).

## Direct division

**[EVIDENCE]** For polynomial modular division `A(z)/B(z) mod P(z)`, the
implicit route constructs the transition sequence for `(P,B)` and applies it
to `(0,A)`. This yields the quotient action without first materializing
`B^-1` and then multiplying. The paper's table reports lower dominant
field-multiplication counts for its direct-division construction than for its
explicit invert-then-multiply construction. See
[page 9](../../source-pages/khattar-2510.10967v1/page-09.md).

This resembles Schrottenloher's replay on an arbitrary coefficient register,
but the fields, transition alphabets, and cost units differ.

## Explicit synchronized EEA

**[EVIDENCE]** The explicit construction stores the quotient inside guaranteed
padding of the shared remainder/coefficient register, avoiding a separate
quotient register. A unified cycle merges division and coefficient-update work
that occurs on different portions of the shared layout. The source states a
worst-case schedule of `6n` iterations and a leading cost of `6n^2`
quantum-quantum multiplications in the base field. See pages
[10](../../source-pages/khattar-2510.10967v1/page-10.md)–[11](../../source-pages/khattar-2510.10967v1/page-11.md)
and the proof route around pages
[41](../../source-pages/khattar-2510.10967v1/page-41.md)–[43](../../source-pages/khattar-2510.10967v1/page-43.md).

**[EVIDENCE]** Register sharing follows polynomial degree invariants, including
that coefficient growth complements remainder shrinkage and creates space for
the quotient. These are polynomial-degree facts, not immediate integer bit
length facts. See [page 11](../../source-pages/khattar-2510.10967v1/page-11.md).

## Dialog representation

**[EVIDENCE]** For a division-free constant-time polynomial EEA, each symbol
describes simple operations such as:

```text
Doubling/shift
Inversion/swap
Addition or subtraction by a field coefficient
```

The name “Dialog” abbreviates these operations. The representation is linear:
symbols correspond to invertible matrix actions, so the sequence can be
applied to arbitrary vectors. See pages
[10](../../source-pages/khattar-2510.10967v1/page-10.md)–[12](../../source-pages/khattar-2510.10967v1/page-12.md).

**[EVIDENCE]** As one Dialog element is appended, active polynomial storage
shrinks by one coefficient. This supports a shared layout near the input-size
bound. See pages
[12](../../source-pages/khattar-2510.10967v1/page-12.md)–[13](../../source-pages/khattar-2510.10967v1/page-13.md).

Reference Python for the synchronized EEA and Dialog construction/consumption
appears on pages
[48](../../source-pages/khattar-2510.10967v1/page-48.md)–[52](../../source-pages/khattar-2510.10967v1/page-52.md).

## Prime-field transfer barrier

The source operates on polynomials over `F_q`. The benchmark operates on
integers modulo the large prime `2^256-2^32-977`.

Before transfer, derive:

```text
integer transition alphabet
sign convention
quotient or branch metadata per step
fixed iteration proof
bit-width growth/shrink invariant
cost of one transition in Toffolis
canonical modular correction
forward and inverse transition order
```

Polynomial shift by `z`, polynomial degree, and multiplication by a base-field
coefficient do not equal integer shift, bit length, and prime-field
multiplication.

## Transfer experiments

- **[INFERENCE]** Treat Schrottenloher's `(b0, b0&b1)` tape as a primitive
  integer Dialog and search for a different small invertible matrix alphabet
  with lower encoded entropy or cheaper replay.
- **[INFERENCE]** Test whether an integer quotient digit can be stored in
  padding made available by a proven bit-length invariant, eliminating a
  separate history segment.
- **[INFERENCE]** Ask whether the benchmark consumer needs an inverse value at
  all. If it needs only `y/x`, direct transition replay may avoid a materialized
  inverse.
- **[INFERENCE]** Prototype the transition semantics classically at small prime
  widths before assigning quantum resource counts.
- **[INFERENCE]** Do not transfer the paper's `2nb` or multiplication-count
  claims numerically. Transfer only the representation principle until an
  integer proof exists.
