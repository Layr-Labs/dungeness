# Häner et al.: integrated elliptic-curve arithmetic

Source: IACR ePrint 2020/077, *Improved quantum circuits for elliptic curve
discrete logarithms*.

## Arithmetic portfolio

**[EVIDENCE]** The paper compares low-width, low-T-count, and low-depth
arithmetic choices instead of selecting one adder for every context. It
includes ripple-style addition, ancilla-assisted addition, carry lookahead,
and two approaches to classical constants: loading a constant into a register
or currying it directly into gates. See
[pages 4–5](../source-pages/haner-2020-077/page-04.md).

**[EVIDENCE]** Its controlled modular addition does not attach the outer
control uniformly to every internal operation. The quantum addition and final
conditional correction carry the needed control, while deterministic modulus
logic remains uncontrolled where the arithmetic implication permits it. See
[page 6](../source-pages/haner-2020-077/page-06.md).

## Montgomery multiplication

**[EVIDENCE]** Values are represented as `x*2^n mod p`. Windowed
add-and-halve multiplication consumes several multiplier bits, performs
shifted additions, chooses a multiple of the modulus that clears low bits, and
rotates the register to divide by the radix. See
[pages 6–7](../source-pages/haner-2020-077/page-06.md).

## Caller-aware uncomputation

**[EVIDENCE]** To compute `xy+z`, the construction keeps multiplication
workspace through the following addition and then reverses the multiplier.
Using the consumer operation in place of a separate copy avoids an additional
forward multiplication. The paper applies the same idea to a
square-then-subtract segment of affine point addition. See
[page 7](../source-pages/haner-2020-077/page-07.md).

## Kaliski inversion and division

**[EVIDENCE]** Four Kaliski round cases are normalized by controlled swaps of
remainder and coefficient pairs. A common subtract, add, halve, and double
body is then executed before swapping back. See
[pages 8–9](../source-pages/haner-2020-077/page-08.md).

**[EVIDENCE]** Fixed `2n` rounds produce a pseudo-inverse with a power-of-two
factor determined by the number of active rounds. During reversal, the same
round controls can drive correcting doublings of the copied result, overlapping
correction with cleanup. See
[page 8](../source-pages/haner-2020-077/page-08.md).

**[EVIDENCE]** In modular division, registers containing known terminal
constants after inversion are cleared and reused as multiplication workspace.
See [pages 8–10](../source-pages/haner-2020-077/page-08.md).

## Coordinates and lookup

**[EVIDENCE]** The paper compares affine and projective coordinates.
Non-unique projective representations make clean in-place use and
uncomputation costly in the analyzed construction, so it retains affine
short-Weierstrass coordinates. See
[pages 15–16](../source-pages/haner-2020-077/page-15.md).

**[EVIDENCE]** Precomputed classical points are loaded at each use and erased
before expensive arithmetic, exchanging repeated lookup work for lower
persistent width. See
[pages 17–18](../source-pages/haner-2020-077/page-17.md).

## Resource interpretation

**[EVIDENCE]** The paper provides separate formula families for low-width,
low-T-count, and low-depth strategies. For a 256-bit curve, its low-width
complete ECDLP construction reports 2,124 logical qubits. See
[pages 19–21](../source-pages/haner-2020-077/page-19.md).

**[EVIDENCE]** Automatic compilation of an out-of-place `xy+z` primitive can
reduce T count and depth while increasing width sharply. At 256 bits, one
table contrasts width 2,319 for the manual construction with 394,588 for the
automatically compiled construction. See
[page 22](../source-pages/haner-2020-077/page-22.md).
