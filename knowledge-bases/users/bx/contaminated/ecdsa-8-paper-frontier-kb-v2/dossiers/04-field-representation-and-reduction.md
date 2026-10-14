# Decision dossier: field representation and reduction

The same mathematical field element can be represented in several circuit
forms. A local multiplication count is meaningful only together with the
representation that enters, leaves, and persists between calls.

## Representations in the source set

| Representation | Source | Benefit | Liability |
|---|---|---|---|
| Canonical residue with pseudo-Mersenne correction | [Schrottenloher](../evidence/papers/01-schrottenloher.md) | secp256k1-specific short correction by `2^32+977` | approximation and boundary cases |
| Montgomery residue | [Litinski](../evidence/papers/02-litinski.md), [Häner](../evidence/papers/08-haner.md) | add-and-halve multiplication, windowed reduction | entry/exit conversion and global consistency |
| Kaliski pseudo-inverse | [Häner](../evidence/papers/08-haner.md) | fixed inversion schedule | power-of-two correction |
| Shared split remainder/coefficient state | [Luo](../evidence/papers/06-luo.md) | low inversion width | location controls and non-public internal form |
| Polynomial residue / Dialog | [Khattar](../evidence/papers/07-khattar.md) | linear transition application | different field and shift semantics |

## Make representation global when possible

Converting around every multiplication usually erases a local advantage.
For a proposed representation, trace the whole affine shell:

```text
target coordinate input
subtract runtime offset
division
squaring
coordinate correction
multiplication
final public output
reverse execution
```

Mark where addition, subtraction, comparison, equality, lookup, and negation
remain valid without conversion.

Montgomery addition is ordinary modular addition on Montgomery residues, so an
entire shell may remain in that form. But the benchmark public ABI may require
canonical coordinates. Cost boundary conversion once, and verify that
runtime-classical offsets are encoded compatibly.

## Pseudo-Mersenne reduction

For secp256k1:

```text
p = 2^256 - f
f = 2^32 + 977
```

Overflow beyond bit 255 can be folded into a short low-word correction by
`f`. Schrottenloher uses this to simplify doubling and controlled modular
addition. The exact circuit still needs:

- enough low bits to absorb carries;
- an overflow/equality convention;
- correct handling of `x+y=p` in early replay;
- cleanup of the reduction flag;
- a quantified approximation policy if comparisons are truncated.

**[INFERENCE]** Separate two questions that the source combines:

1. Can special-prime reduction be exact and still cheap under this benchmark?
2. If approximation is allowed, what error budget maximizes expected score
   while passing validation?

## Redundant ranges

Keeping values in `[0,2p)` or another redundant interval can remove repeated
canonical corrections, but changes:

```text
comparison semantics
zero and equality tests
negation
input range to multiplication
number of folds needed
reverse cleanup
```

**[INFERENCE]** Test redundancy at a whole sequence boundary, such as all
replay updates, rather than after one addition. The benefit appears only if
several reductions are deferred.

## Representation compatibility ledger

For each primitive, record:

| Primitive | Input range/form | Output range/form | Flag/garbage | Inverse form |
|---|---|---|---|---|
| add/sub | | | | |
| multiply | | | | |
| square | | | | |
| inverse/divide | | | | |
| compare/equality | | | | |
| lookup offset | | | | |

Two primitives compose only when output and input rows match or an explicit
bridge is costed.

## Experiments

1. Measure dynamic reduction/correction calls in the current complete shell.
2. Group adjacent operations and identify corrections that can be deferred.
3. Build an exact small-width pseudo-Mersenne fold and exhaustive-test every
   boundary.
4. Compare canonical, redundant, and Montgomery forms for the complete group
   of calls, including conversion and reverse.
5. Re-measure the hard-ID peak; Montgomery and fresh-output multiplication may
   introduce extra accumulators.

## Transfer warning

Khattar's polynomial Dialog is evidence for a representation method, not for
prime-field arithmetic counts. Polynomial degree shrinkage, division by `z`,
and multiplication by a base-field coefficient require a new integer proof
before use on secp256k1.
