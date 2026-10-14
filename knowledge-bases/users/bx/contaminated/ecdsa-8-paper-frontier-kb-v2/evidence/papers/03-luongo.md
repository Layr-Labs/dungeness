# Luongo et al.: measurement-based uncomputation for modular arithmetic

Source: arXiv:2407.20167v1, *Measurement-based uncomputation of quantum
circuits for modular arithmetic*.

## Operational role

This paper supplies a systematic rule for deleting a one-bit function by
measurement and paying for its recomputation only on one measurement outcome.
It then applies that rule to comparator flags in modular adders and controlled
modular adders.

The useful unit is not “measurement makes cleanup free.” It is:

```text
identify a self-inverse recomputation Ug for one garbage bit
measure the bit in the Hadamard basis
with probability 1/2, finish
otherwise invoke Ug to repair phase and reset
```

Therefore the savings are expected savings in a specific inverse subroutine.

## Baseline modular-adder architecture

**[EVIDENCE]** The VBE-style modular adder performs:

1. quantum addition;
2. comparison with the classical modulus;
3. conditional subtraction of the modulus;
4. a second comparison that erases the reduction flag using the reduced
   output.

The identity used for cleanup is that, for valid inputs below `p`, the overflow
condition can be recovered from whether the reduced result is below an addend.
See pages [24](../../source-pages/luongo-2407.20167v1/page-24.md)–[26](../../source-pages/luongo-2407.20167v1/page-26.md).

**[EVIDENCE]** Reported non-MBU choices include:

| Construction | Ancillas | Toffoli |
|---|---:|---:|
| CDKPM | `n+3` | `8n` |
| Gidney | `2n+3` | `4n` |
| hybrid | `n+3` | `6n` |

See pages [26](../../source-pages/luongo-2407.20167v1/page-26.md)–[27](../../source-pages/luongo-2407.20167v1/page-27.md).

## Controlled structure

**[EVIDENCE]** A controlled modular adder does not control every subroutine.
Only the first addition and final cleanup comparison need the outer control;
the modulus comparison and reduction subtraction follow from the resulting
value and their own flag. Reported non-MBU costs include `9n+1` Toffolis for
the CDKPM version and `5n+1` for the Gidney version. See pages
[28](../../source-pages/luongo-2407.20167v1/page-28.md)–[30](../../source-pages/luongo-2407.20167v1/page-30.md).

This is independently useful even when measurement is unavailable: it exposes
which operations actually depend on the external control.

## Measurement-based uncomputation lemma

**[EVIDENCE]** For a Boolean garbage function `g(x)`, the paper measures its
qubit after a Hadamard. One outcome resets it directly. The other leaves a
phase `(-1)^g(x)`; applying the self-adjoint computation `Ug`, with single
qubit Clifford corrections, cancels the phase and returns the target to zero.
Thus `Ug` is invoked with probability one half. See
[page 34](../../source-pages/luongo-2407.20167v1/page-34.md) and
[page 35](../../source-pages/luongo-2407.20167v1/page-35.md).

The preconditions matter:

- garbage is one Boolean function of still-available data;
- the repair computation has the required self-inverse behavior;
- the classical measurement outcome survives until feed-forward;
- expected executed cost, not worst-case static gate count, is the claimed
  improvement.

## Reported MBU costs

**[EVIDENCE]** Applying MBU only to the final comparator gives expected costs:

| Modular adder | Expected Toffoli | Ancillas |
|---|---:|---:|
| CDKPM | `7n` | `n+3` |
| Gidney | `3.5n` | `2n+3` |
| hybrid | `5.5n` | `n+3` |

See pages [35](../../source-pages/luongo-2407.20167v1/page-35.md)–[37](../../source-pages/luongo-2407.20167v1/page-37.md).

**[EVIDENCE]** Controlled variants include expected `8n+0.5` for CDKPM and
`4.5n+0.5` for Gidney. The same pattern is developed for constant and
controlled-constant modular addition. See pages
[37](../../source-pages/luongo-2407.20167v1/page-37.md)–[40](../../source-pages/luongo-2407.20167v1/page-40.md).

**[EVIDENCE]** A two-sided comparator can similarly save 25% of the relevant
comparison cost by measuring an intermediate comparison flag. See pages
[40](../../source-pages/luongo-2407.20167v1/page-40.md)–[41](../../source-pages/luongo-2407.20167v1/page-41.md).

## Transfer barriers and experiments

- **[INFERENCE]** Search for one-bit cleanup functions in the current dominant
  modular primitive. Measure the exact inverse subroutine cost before applying
  the 1/2 factor.
- **[INFERENCE]** Prefer flags whose source registers remain live and whose
  repair does not raise the hard allocation peak.
- **[INFERENCE]** Compare MBU with algebraic cleanup. A cheaper comparison
  identity may beat measurement even if both are correct.
- **[INFERENCE]** Combine the paper's “control only the boundary operations”
  observation with Gidney's no-extra-Toffoli controlled constant adder.
- **[INFERENCE]** Do not extrapolate a one-bit expected-cleanup lemma to a full
  transcript or field register. For larger demolition use the explicit
  register-phase protocols in the Gidney, Luo, or Spooky evidence cards.
