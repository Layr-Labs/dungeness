# Häner et al.: mature affine stack, Montgomery arithmetic, and pebbling

Source: IACR ePrint 2020/077, *Improved quantum circuits for elliptic curve
discrete logarithms*.

## Operational role

This paper is a mature end-to-end architecture study. It is useful for:

- alternative low-width, low-T, and low-depth component choices;
- controlled and constant arithmetic interfaces;
- Montgomery multiplication;
- a swap-normalized Kaliski inversion;
- workspace reuse in modular division;
- pebbling at the affine-shell level;
- warnings about coordinate and representation conversions.

Its resource metric is primarily T count/depth and logical width. Translation
to benchmark average Toffoli and maximum referenced ID remains necessary.

## Arithmetic portfolio

**[EVIDENCE]** The paper explicitly keeps multiple design points rather than a
single globally best adder: low-width TTK-style addition, low-T
Gidney/CDKM-style addition with ancillas, and low-depth carry lookahead. It
describes two ways to add a classical constant: load it into a quantum register
and use an ordinary adder, or curry the constant into the gates. See pages
[4](../../source-pages/haner-2020-077/page-04.md)–[5](../../source-pages/haner-2020-077/page-05.md).

**[EVIDENCE]** Controlled modular addition need not control every internal
operation. The paper's circuit controls the quantum addition and the final
conditional correction structure while leaving deterministic modulus logic
uncontrolled where valid. See
[page 6](../../source-pages/haner-2020-077/page-06.md).

## Montgomery multiplication

**[EVIDENCE]** Values are represented as `x*2^n mod p`. The multiplier follows
add-and-halve Montgomery arithmetic. A window takes several multiplier bits,
uses them for shifted addition, derives a table-selected multiple of `p` that
clears low bits, then rotates to divide by the radix. See pages
[6](../../source-pages/haner-2020-077/page-06.md)–[7](../../source-pages/haner-2020-077/page-07.md).

Changing a canonical-field benchmark implementation to this multiplier is a
global representation decision unless entry/exit conversions are explicitly
costed.

## Local pebbling

**[EVIDENCE]** To compute `xy+z`, the paper keeps the product workspace live
through the following addition and then reverses the multiplier. Replacing a
copy step with the consumer addition avoids a second forward multiplication.
The same idea reduces the square-then-subtract portion of affine point
addition and can remove an auxiliary register. See
[page 7](../../source-pages/haner-2020-077/page-07.md).

This is a concrete caller-aware optimization: cost the producer together with
its sole consumer before choosing an output ABI.

## Kaliski inversion and division

**[EVIDENCE]** The paper reformulates four Kaliski round cases by controlled
swapping the appropriate remainder/coefficient pairs, executing one common
subtract/add/halve/double body, and swapping back. See pages
[8](../../source-pages/haner-2020-077/page-08.md)–[9](../../source-pages/haner-2020-077/page-09.md).

**[EVIDENCE]** Fixed `2n` rounds produce a pseudo-inverse whose power-of-two
factor depends on the number of active rounds. During reverse inversion, the
same round control can drive corrective doublings of the copied output, placing
correction in parallel with cleanup. See
[page 8](../../source-pages/haner-2020-077/page-08.md).

**[EVIDENCE]** In modular division, registers holding known terminal constants
from inversion are cleared and reused as multiplication workspace rather than
allocating an independent multiplier area. See pages
[8](../../source-pages/haner-2020-077/page-08.md)–[10](../../source-pages/haner-2020-077/page-10.md).

## Coordinate and lookup decisions

**[EVIDENCE]** The paper evaluates affine and projective coordinate choices.
Projective outputs have non-unique representations, making clean in-place
use and uncomputation expensive; the analyzed conversion can require forward
and reverse point-addition work plus division. It therefore retains affine
short-Weierstrass coordinates. See pages
[15](../../source-pages/haner-2020-077/page-15.md)–[16](../../source-pages/haner-2020-077/page-16.md).

**[EVIDENCE]** Precomputed-point lookups can be loaded only at each use and
uncomputed before expensive arithmetic, trading repeated lookup cost for no
additional persistent coordinate registers. See pages
[17](../../source-pages/haner-2020-077/page-17.md)–[18](../../source-pages/haner-2020-077/page-18.md).

## Resource interpretation

**[EVIDENCE]** The paper reports formulas and numerical fits for low-width,
low-T, and low-depth strategies. Its low-width signed-window point addition has
a width around eight `n`-scale units plus logarithmic terms in the source's
logical-width model; the exact tables are on pages
[19](../../source-pages/haner-2020-077/page-19.md)–[21](../../source-pages/haner-2020-077/page-21.md).

**[EVIDENCE]** Automatic compilation can sharply lower T count/depth for an
out-of-place `xy+z` unitary while increasing width by orders of magnitude. At
256 bits, the source table contrasts a manual width of 2,319 with an automatic
width of 394,588 for that primitive. See
[page 22](../../source-pages/haner-2020-077/page-22.md).

This is a useful extreme point: local T minimization can be catastrophic for a
T×Q objective.

## Transfer barriers and experiments

- **[INFERENCE]** Re-evaluate the swap-normalized Kaliski body using current
  constant-add and MBU primitives rather than copying its 2020 component
  portfolio unchanged.
- **[INFERENCE]** Apply multiply-then-consume pebbling to the exact dominant
  caller in the benchmark. Look for a temporary used once before reverse.
- **[INFERENCE]** Move pseudo-inverse correction into reverse cleanup whenever
  control signals are already available.
- **[INFERENCE]** Search for terminal known constants inside inversion that can
  be cleared and reused at the hard-ID interval.
- **[INFERENCE]** Treat Montgomery conversion as global: compare a complete
  shell that remains in Montgomery form, not one isolated multiplication.
- **[INFERENCE]** Use the paper's coordinate rejection as a checklist, not a
  permanent theorem. A different benchmark ABI or measurement protocol could
  change the cost of making projective outputs unique.
