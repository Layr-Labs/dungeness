# Litinski: controlled add-subtract multiplication

Source: arXiv:2410.00899v1, *Quantum schoolbook multiplication with fewer
Toffoli gates*.

## Operational role

This paper changes the control structure of schoolbook multiplication. Instead
of conditionally adding a shifted multiplicand or doing nothing, each bit
selects between addition and subtraction. The main multiplication work becomes
cheaper, at the price of global algebraic corrections.

It is a strong source of arithmetic hypotheses, but its main interfaces are
fresh-output multiplication and Montgomery modular multiplication. Those do
not automatically fit an in-place canonical-field point-addition spine.

## Primitive contract

**[EVIDENCE]** The non-modular primitive is:

```text
|x>|y>|0_(2n)> -> |x>|y>|xy>
```

A controlled add-subtract adds when its control is one and subtracts when the
control is zero. With carry-out it costs `n` Toffolis; without carry-out it
costs `n-1`, matching an uncontrolled adder in the paper's construction. See
[page 1](../../source-pages/litinski-2410.00899v1/page-01.md).

This differs from a controlled adder:

```text
control = 1 -> add
control = 0 -> no-op
```

The add-subtract primitive instead performs useful but unwanted work on the
zero branch, and later removes its aggregate effect.

## Algebraic correction

**[EVIDENCE]** After the shifted add-subtract sequence, the intermediate value
is:

```text
2xy + 2^(2n) - 2^n(x + 1 + y) + y
```

The construction then adds `2^n(x+1)`, subtracts `2^(2n)+y`, adds `2^n y`, and
divides by two by relabeling qubits. The stated total is
`n^2 + 4n + 3` Toffolis, compared with the paper's `2n^2+n` standard
schoolbook count. See
[page 2](../../source-pages/litinski-2410.00899v1/page-02.md).

**[EVIDENCE]** For multiplication modulo `2^n`, truncation simplifies the
global corrections and gives `0.5n^2 + 1.5n` Toffolis. This ring is not the
secp256k1 prime field; the result is useful as a structural example rather than
a directly importable field multiplier. See
[page 2](../../source-pages/litinski-2410.00899v1/page-02.md).

## Prime-modulus construction

**[EVIDENCE]** The prime-modulus construction is an out-of-place Montgomery
multiplier divided into `n/w` `ModMultStep` windows. Each window uses shifted
controlled add-subtracts, lookup-based reduction data, corrections, and a
divide-by-two relabeling. The paper gives:

```text
n^2 + 6n + (n/w) * (2^w + 3*2^(w/2) + 3n - 3)
```

Toffolis, with an approximate optimizing window
`w ≈ log2(n/log2 n) + 2`. See pages
[2](../../source-pages/litinski-2410.00899v1/page-02.md)–[4](../../source-pages/litinski-2410.00899v1/page-04.md).

**[EVIDENCE]** Each window emits `w` garbage qubits in the described
construction. To erase multiplication garbage, the paper proposes copying the
fresh result to another register and reversing the full multiplication. See
[page 2](../../source-pages/litinski-2410.00899v1/page-02.md).

## Why local counts can mislead

- The output is fresh, so peak live width includes input factors, the result,
  window state, and possibly a copied result during cleanup.
- Values are in Montgomery representation.
- The advertised cost is for the forward multiplier; a clean reusable
  interface may require copy/uncompute.
- Replacing one controlled-adder loop inside an existing multiplier does not
  work unless the global correction identity remains valid across the complete
  accumulator.

## Transfer barriers and experiments

- **[INFERENCE]** First search existing benchmark code for a full shifted
  controlled-add loop whose output is allowed to be fresh. Test the transformed
  algebra at small widths before building quantum gates.
- **[INFERENCE]** If the current architecture is in place, compare three
  complete bridges: fresh product plus swap/uncompute, use inside a temporary
  square, and conversion of an entire affine shell to fresh-output dataflow.
- **[INFERENCE]** Test whether runtime-classical multiplicands simplify the
  correction terms more than the paper's quantum-quantum setting.
- **[INFERENCE]** A hybrid may use add-subtract only over a contiguous subset
  of multiplier bits and correct its signed block globally. The correction
  must be derived, not applied bitwise.
- **[INFERENCE]** Compare the Q increase at the actual hard-ID interval. The
  asymptotic T win may still improve the product if the fresh register fits
  into workspace already live but unused.

## Evidence route

- Primitive and count table:
  [page 1](../../source-pages/litinski-2410.00899v1/page-01.md)
- Correction identity and modulo-`2^n` variant:
  [page 2](../../source-pages/litinski-2410.00899v1/page-02.md)
- Baseline `ModMultStep`:
  [page 3](../../source-pages/litinski-2410.00899v1/page-03.md)
- Add-subtract Montgomery step and total:
  [page 4](../../source-pages/litinski-2410.00899v1/page-04.md)
- Application-level comparison:
  [page 5](../../source-pages/litinski-2410.00899v1/page-05.md)
