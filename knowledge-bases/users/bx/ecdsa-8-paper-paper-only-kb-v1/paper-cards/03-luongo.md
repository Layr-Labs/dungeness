# Luongo et al.: measurement-based uncomputation

Source: arXiv:2407.20167v1, *Measurement-based uncomputation of quantum
circuits for modular arithmetic*.

## One-bit uncomputation lemma

**[EVIDENCE]** Suppose a self-adjoint unitary computes a Boolean function:

```text
Ug |x>|b> = |x>|b xor g(x)>.
```

For a state whose final qubit stores `g(x)`, Hadamard-basis measurement can
reset that qubit. One outcome finishes with Clifford corrections only. The
other leaves phase `(-1)^g(x)` and invokes `Ug` to repair it. The expensive
repair is therefore needed with probability one half. See
[pages 34–35](../source-pages/luongo-2407.20167v1/page-34.md).

**[EVIDENCE]** The retained data must still determine `g(x)`, the measurement
outcome must remain available for feed-forward, and the claimed saving is an
expected invocation count for the specified cleanup unitary. See
[pages 34–35](../source-pages/luongo-2407.20167v1/page-34.md).

## Modular-adder structure

**[EVIDENCE]** The modular adder studied in the paper performs ordinary
addition, compares with the classical modulus, conditionally subtracts the
modulus, and computes a second predicate that erases the reduction flag. For
inputs below the modulus, that final predicate can be recovered from the
reduced output and an addend. See
[pages 24–26](../source-pages/luongo-2407.20167v1/page-24.md).

**[EVIDENCE]** The paper reports the following non-measurement counts:

| Construction | Ancillas | Toffolis |
|---|---:|---:|
| CDKPM modular addition | `n+3` | `8n` |
| Gidney modular addition | `2n+3` | `4n` |
| mixed construction | `n+3` | `6n` |

See [pages 26–27](../source-pages/luongo-2407.20167v1/page-26.md).

## Controlled structure

**[EVIDENCE]** In the controlled modular adder, the outer control is not
attached to every internal operation. The initial addition and final cleanup
predicate depend on it, while modulus comparison and reduction are driven by
the resulting value and their own flag. See
[pages 28–30](../source-pages/luongo-2407.20167v1/page-28.md).

## Expected costs with measurement

**[EVIDENCE]** Applying the one-bit lemma to the final comparison gives:

| Modular adder | Expected Toffolis | Ancillas |
|---|---:|---:|
| CDKPM | `7n` | `n+3` |
| Gidney | `3.5n` | `2n+3` |
| mixed | `5.5n` | `n+3` |

See [pages 35–37](../source-pages/luongo-2407.20167v1/page-35.md).

**[EVIDENCE]** Controlled versions include expected counts of `8n+0.5` for
the CDKPM construction and `4.5n+0.5` for the Gidney construction. The paper
also develops constant and controlled-constant modular adders using the same
method. See
[pages 37–40](../source-pages/luongo-2407.20167v1/page-37.md).

**[EVIDENCE]** A related two-sided comparator measures an intermediate
comparison flag and reduces the relevant expected comparison work by 25%. See
[pages 40–41](../source-pages/luongo-2407.20167v1/page-40.md).
