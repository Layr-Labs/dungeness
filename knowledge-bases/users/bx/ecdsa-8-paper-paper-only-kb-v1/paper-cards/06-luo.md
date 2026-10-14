# Luo et al.: exact shared-register EEA

Source: arXiv:2607.13816v2, *Quantum Algorithm for Elliptic Curve Discrete
Logarithms with Space-Efficient Point Addition*.

## Four-phase Euclidean schedule

**[EVIDENCE]** The reversible extended Euclidean algorithm separates each
quotient update into four phases:

1. shift the active remainder while increasing a shift counter;
2. form quotient bits while subtracting shifted remainders;
3. consume quotient bits while updating a coefficient;
4. restore coefficient alignment and complete the iteration.

Different basis states may occupy different phases at the same circuit step.
The paper nevertheless proves a common upper bound

```text
4 ceil(cn), where c = 3/log2(2+sqrt(3)),
```

which is below `6.316n` elementary steps. See
[pages 10–13](../source-pages/luo-2607.13816v2/page-10.md).

**[EVIDENCE]** The forward inversion subroutine has the form

```text
|x>|0^n>|0^m> -> |x^-1 mod p>|0^n>|Gamma(x)>.
```

It conditionally replaces `x` by `p-x` when `x>p/2` and retains a parity bit
needed to reverse the transformation. See
[page 13](../source-pages/luo-2607.13816v2/page-13.md).

## Shared registers

**[EVIDENCE]** The invariant

```text
r_(i-1)t_i + r_i t_(i-1) = p
```

supports complementary storage of shrinking remainders and growing
coefficients. One work register stores portions of a coefficient, quotient,
and remainder; the second stores the other coefficient and remainder. Four
logarithmic length registers track changing boundaries. See
[pages 14–16](../source-pages/luo-2607.13816v2/page-14.md).

**[EVIDENCE]** Additions, subtractions, swaps, and length updates act on
coherently selected active ranges. The paper derives range bounds for each
phase and implements the selections with unary iteration controls. See
[pages 18–29](../source-pages/luo-2607.13816v2/page-18.md).

## Full-register measurement and repair

**[EVIDENCE]** The paper constructs in-place modular division and
multiplication with three field-sized registers:

```text
IDiv: |x>|y>|0> -> |x>|y/x>|0>
IMul: |x>|y>|0> -> |x>|xy>|0>.
```

For division, it computes a quotient into the auxiliary register, measures and
resets the obsolete `y` register in the Hadamard basis, uses that clean
register to reverse the EEA, reconstructs the old `y`, applies the
measurement-dependent phase correction, uncomputes the reconstruction, and
places the quotient in the output register. See
[pages 30–31](../source-pages/luo-2607.13816v2/page-30.md).

## Resource statements

**[EVIDENCE]** The stated logical widths are

```text
modular inversion: 2n + 6 floor(log2 n) + 19
point addition:    3n + 6 floor(log2 n) + 19.
```

See [page 32](../source-pages/luo-2607.13816v2/page-32.md).

**[EVIDENCE]** The paper bounds inversion below
`216.636n^2 + O(n log n)` Toffolis and point addition below
`1003n^2 + O(n log n)`. At `n=256`, its compiled tables report 579 qubits and
30.59 million Toffolis for inversion, and 835 qubits and 70.10 million
Toffolis for controlled point addition. See
[pages 33–35](../source-pages/luo-2607.13816v2/page-33.md).

## Scope

**[EVIDENCE]** The construction depends on logarithmic phase and length
metadata, location-controlled arithmetic, and explicit phase repair after
measurement. These components are part of the stated space bound and
reversibility argument. See
[pages 14–32](../source-pages/luo-2607.13816v2/page-14.md).
