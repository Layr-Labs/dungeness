# Luo et al.: exact shared-register EEA and full-register demolition

Source: arXiv:2607.13816v2, *Quantum Algorithm for Elliptic Curve Discrete
Logarithms with Space-Efficient Point Addition*.

## Operational role

This paper offers a deliberately different point in the design space from the
compact-history spine:

- exact fixed-step EEA;
- two large shared work registers plus logarithmic metadata;
- no large branch transcript;
- active-window arithmetic;
- full-register measurement and phase repair to obtain three-field-register
  in-place multiplication and division.

It is particularly useful for separating transcript space from arithmetic cost.

## Four-phase exact EEA

**[EVIDENCE]** The algorithm implements quotient extraction and coefficient
updates through four phases:

1. left-shift the current remainder while increasing a shift counter;
2. right-shift and form quotient bits while subtracting shifted remainders;
3. consume quotient bits while adding shifted coefficients;
4. right-shift the coefficient register back and complete the iteration.

Input branches can be in different EEA iterations and phases at the same global
step. Nevertheless, the paper proves a common fixed bound:

```text
4 ceil(c n) steps, c = 3/log2(2+sqrt(3)), below 6.316 n
```

See pages [10](../../source-pages/luo-2607.13816v2/page-10.md)–[13](../../source-pages/luo-2607.13816v2/page-13.md).

**[EVIDENCE]** The forward subroutine maps:

```text
|x>|0^n>|0^m> -> |x^-1 mod p>|0^n>|Gamma(x)>
```

It conditionally replaces `x` by `p-x` when `x>p/2` and retains an iteration
parity bit so the map remains invertible. See
[page 13](../../source-pages/luo-2607.13816v2/page-13.md).

## Register sharing and invariants

**[EVIDENCE]** The identity:

```text
r_(i-1) t_i + r_i t_(i-1) = p
```

supports complementary storage of shrinking remainders and growing
coefficients. `Work1` stores portions of `t`, the current quotient, and `r`;
`Work2` stores `t'` and `r'`, sometimes with `t'` split across the two ends of
a circularly shifted register. Four logarithmic length registers track the
boundaries. See pages
[14](../../source-pages/luo-2607.13816v2/page-14.md)–[16](../../source-pages/luo-2607.13816v2/page-16.md).

**[EVIDENCE]** Arithmetic is location-controlled: additions, subtractions,
swaps, and length updates act only on a coherently selected active range. The
paper derives per-step active-window bounds and uses unary iteration controls
to implement location-dependent operations. See pages
[18](../../source-pages/luo-2607.13816v2/page-18.md)–[29](../../source-pages/luo-2607.13816v2/page-29.md).

## Three-register in-place division

**[EVIDENCE]** The abstract interface is:

```text
IDiv: |x>_X |y>_Y |0>_A -> |x>_X |y/x>_Y |0>_A
IMul: |x>_X |y>_Y |0>_A -> |x>_X |xy>_Y  |0>_A
```

For division:

1. run forward EEA on `X`, using `A` as large workspace;
2. compute `y/x` into `A`;
3. Hadamard-measure and reset the old `Y`, retaining outcome `b`;
4. use clean `Y` to reverse EEA and restore `x`;
5. recompute old `y` from `x` and `y/x`;
6. apply `Z_b` to cancel phase `(-1)^(b dot y)`;
7. uncompute recreated `y` and swap result into `Y`.

See pages [30](../../source-pages/luo-2607.13816v2/page-30.md)–[31](../../source-pages/luo-2607.13816v2/page-31.md).

This is exact full-register demolition with explicit recomputation, not a
one-bit expected-cost shortcut.

## Resource point

**[EVIDENCE]** The stated logical widths are:

```text
inversion:      2n + 6 floor(log2 n) + 19
point addition: 3n + 6 floor(log2 n) + 19
```

See [page 32](../../source-pages/luo-2607.13816v2/page-32.md).

**[EVIDENCE]** The one-sided inversion asymptotic bound is below
`216.636 n^2` Toffolis. The full point-addition accounting includes multiple
inversions/divisions and multiplications and is below `1003 n^2` in the stated
model. At `n=256`, the compiled table reports 30.59 million Toffolis for
inversion and 70.10 million for point addition. See pages
[33](../../source-pages/luo-2607.13816v2/page-33.md)–[35](../../source-pages/luo-2607.13816v2/page-35.md).

The paper optimizes space, not the benchmark product. High T is an explicit
liability.

## Transfer barriers and experiments

- **[EVIDENCE]** The EEA ABI includes logarithmic length/phase metadata and
  location-controlled arithmetic; it is not a drop-in replacement for a branch
  tape.
- **[EVIDENCE]** The demolition protocol requires an entire clean field
  register after measurement and an explicit recomputation of the old value.
- **[INFERENCE]** Isolate the demolition wrapper from the expensive EEA. Test
  it around a cheaper in-place or out-of-place multiplier already present.
- **[INFERENCE]** Compare exact active-window arithmetic with probabilistic
  shrinking-register padding. The exact scheduler may reduce failure risk but
  add control overhead.
- **[INFERENCE]** Borrow the register-layout invariant without borrowing the
  four-phase recurrence, or borrow the four-phase recurrence while replaying a
  cheaper transition representation.
- **[INFERENCE]** Use this as a lower-Q reference point: if the current hard-ID
  owner remains well above three field registers, identify exactly which
  metadata or wrapper prevents the same lifetime pattern.
