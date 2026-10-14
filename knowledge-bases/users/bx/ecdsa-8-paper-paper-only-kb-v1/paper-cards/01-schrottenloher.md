# Schrottenloher: compact Euclid history and linear replay

Source: arXiv:2606.02235v1, *Optimized Point Addition Circuits for Elliptic
Curve Discrete Logarithms*.

## Affine point addition

**[EVIDENCE]** The paper works with affine short-Weierstrass points over a
prime field. For secp256k1 it uses

```text
q = 2^256 - 2^32 - 977
a = 0
b = 7
```

and organizes point addition around modular subtraction, squaring, and
in-place multiplication or division. The two coordinate registers are updated
in place while selected classical points are loaded and later erased. See
[pages 6–8](../source-pages/schrottenloher-2606.02235v1/page-06.md).

## Binary-Euclid transcript

**[EVIDENCE]** A fixed iteration computes two branch indicators and updates
the Euclidean pair:

```text
b0 = parity(v)
b1 = (u > v)
record b0 and (b0 & b1)
if b0 & b1: swap(u,v)
if b0:      v <- v-u
v <- floor(v/2)
```

The paper estimates an average length near `1.413n`, with standard deviation
near `0.6 sqrt(n)`, and pads the circuit to a fixed length. See
[pages 9–10](../source-pages/schrottenloher-2606.02235v1/page-09.md).

**[EVIDENCE]** Three iterations produce only 27 valid six-bit branch patterns.
The paper encodes each triple in five bits with a reversible compressor. This
gives a transcript of approximately `2.355n + O(sqrt(n))` bits, compared with
an information estimate near `2.12n + O(sqrt(n))`. Shrinking Euclidean
registers share storage with the growing transcript. See
[page 10](../source-pages/schrottenloher-2606.02235v1/page-10.md).

## Replay as multiplication

**[EVIDENCE]** Reading the transcript in reverse controls linear coefficient
updates:

```text
s <- 2s mod q
if b0:       s <- s+r mod q
if b0 & b1: swap(r,s)
```

Because the update is linear, replay can begin from an arbitrary field value
instead of from one. With the ordering used in the paper, this applies the
Euclidean transformation to that value and realizes modular multiplication.
See [page 11](../source-pages/schrottenloher-2606.02235v1/page-11.md).

**[EVIDENCE]** The complete interface converts one operand to its transcript,
replays the transcript on the other operand, and reverses the conversion:

```text
|x>|y> -> |x>|x*y mod q>
```

The inverse circuit realizes multiplication by `x^-1`. See
[page 12](../source-pages/schrottenloher-2606.02235v1/page-12.md).

## Space and arithmetic

**[EVIDENCE]** During replay, two field registers coexist with the compact
transcript, producing the leading space estimate
`4.355n + O(sqrt(n))`. The forward and reverse Euclidean phases have more
temporary space available than replay. See
[page 12](../source-pages/schrottenloher-2606.02235v1/page-12.md).

**[EVIDENCE]** The arithmetic layer combines low-ancilla and
ancilla-assisted adders according to available space. It also uses truncated
comparisons and identities for primes of the form `2^u-f`, replacing selected
corrections by the short constant `f`. See
[pages 13–16](../source-pages/schrottenloher-2606.02235v1/page-13.md).

**[EVIDENCE]** Early replay has a non-random boundary case in which two values
can sum exactly to the modulus. The paper supplies a separate controlled
addition treatment for this case instead of applying the generic
approximation. See
[pages 14–17](../source-pages/schrottenloher-2606.02235v1/page-14.md).

## Reported resources and boundaries

**[EVIDENCE]** For secp256k1, the paper reports approximately 1,192 qubits and
`2^21.19` Toffoli-like gates for its space-oriented point-addition design, and
approximately 1,446 qubits and `2^20.83` gates for its gate-oriented design.
The in-place multiplication and inverse account for about 90% of the reported
gate total. See
[pages 17–18](../source-pages/schrottenloher-2606.02235v1/page-17.md).

**[EVIDENCE]** Several arithmetic reductions are probabilistic and are tested
over sampled inputs. Their error assumptions, fixed padding, and operation
counting belong to the paper's stated model. See
[pages 13–18](../source-pages/schrottenloher-2606.02235v1/page-13.md).
