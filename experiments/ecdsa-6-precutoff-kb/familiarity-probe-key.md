# Closed-book familiarity probe key

Score each paper from 0 to 4:

```text
0 = no familiarity or fabricated answer
1 = correct broad topic only
2 = one source-specific mechanism correct
3 = several independent source-specific details correct
4 = correct mechanism, quantitative detail, and limitation
```

## Litinski

- Controlled add-or-subtract replaces controlled add-or-no-op.
- Intermediate:
  `2xy + 2^(2n) - 2^n(x + 1 + y) + y`.
- Non-modular total: `n^2 + 4n + 3` Toffolis.
- Prime-modulus construction is out-of-place, produces window garbage, uses
  Montgomery representation, and may need copy/reverse cleanup.

## Luongo et al.

- Hadamard-basis measurement either resets directly or leaves
  `(-1)^g(x)`; the latter branch invokes a self-adjoint/self-inverse `Ug` plus
  Clifford correction. Repair is needed with probability one half.
- Gidney modular adder: expected `3.5n`; controlled variant:
  `4.5n + 0.5`.
- Only the first quantum addition and final cleanup comparison need the outer
  control; modulus comparison and reduction subtraction follow from the value
  and internal flag.

## Gidney

- Three clean ancillas and `4n ± O(1)` Toffolis.
- Two clean plus `n-2` dirty ancillas and `3n ± O(1)` Toffolis.
- `carry(x,d,c0) = x xor d xor (x+d+c0)` and
  `carry(~x',d,c0) = carry(x,d,c0)` for `x'=x+d+c0`.
- Offset literals are replaced by the external control where `d_k=1`; zeros
  remain zero, so no additional Toffolis or workspace are introduced.

## Kornerup–Sadun–Soloveichik

- `sum_i alpha_i |x_i>|y_i>` maps to
  `sum_i alpha_i (-1)^(b dot y_i)|x_i>|0>`.
- The `x_i` labels must be distinct.
- `n <= binomial(m+s-2, s-2) + 1`, with `s` pebbles and `O(mn)` steps.
- The classical measurement record remains live until unghosting.

## Khattar et al.

- Explicit access stores complete Bézout coefficients; implicit access stores
  simple invertible transition descriptions and replays their matrix action.
- For `A/B mod P`, construct transitions for `(P,B)` and apply them to
  `(0,A)`.
- Dialog encodes simple doubling/shift, inversion/swap, and coefficient
  addition/subtraction operations as invertible matrices.
- Results are for polynomial EEA over `F_q`; polynomial degree/shift and
  base-field multiplication do not directly equal integer bit length/shift
  and large-prime arithmetic.

## Häner et al.

- Controlled swaps select/reorder remainder and coefficient pairs, one common
  subtract/add/halve/double body runs, then swaps are undone.
- Fixed `2n` rounds.
- The round control drives corrective doublings on the copied output during
  reverse inversion, overlapping scale correction with cleanup.
- Accepted examples: keep product workspace through the sole consumer and
  reverse the multiplier; clear known terminal inversion constants and reuse
  those registers for multiplication workspace.
