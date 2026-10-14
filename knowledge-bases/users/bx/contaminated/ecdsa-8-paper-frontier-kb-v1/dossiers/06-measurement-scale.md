---
kind: research-dossier
id: measurement-scale
depends_on: [information-location, output-placement-and-affine-dataflow]
---

# Dossier: how much garbage should be measured?

The four measurement-oriented papers cover different scales of obsolete data.
They share a phase principle but not a common cost.

## Scale ladder

| Measured object | Source | Later repair |
|---|---|---|
| One Boolean garbage bit | Luongo | conditionally invoke a self-adjoint predicate oracle |
| A stream of obsolete carries | Gidney | carry-xor phase repair, possibly using dirty halves |
| A complete field register | Luo | recompute the exact old value, apply bitwise outcome-controlled Z, uncompute |
| A wide computation checkpoint | Spooky Pebbling | recompute dependency state and unghost the checkpoint |

**[PAPER: Luongo]** One X-basis outcome needs no expensive oracle and the other
does, giving one-half expected oracle use.

**[PAPER: Gidney]** Carries are vented as the ripple advances; classical
measurement outcomes become deferred carry-phase tasks. Dirty target halves can
supply the repair workspace.

**[PAPER: Luo]** Hadamard measurement of `n` old value bits creates phase
`(-1)^(b dot y)`. Exact recomputation of `y` permits bitwise correction.

**[PAPER: Spooky Pebbling]** A ghost lowers coherent checkpoint storage, but
classical information and future recomputation remain.

## Economic rule

**[INFERENCE]**

```text
benefit =
  coherent uncomputation avoided
  + hard-ID reduction from earlier release

cost =
  predicate or checkpoint recomputation
  + conditional phase repair
  + transcript handling
  + explicit reverse protocol
```

Larger measured objects are not automatically better. Their phase predicates
usually depend on more surviving computation.

## Selection questions

- Is the obsolete value exactly recomputable, or only statistically likely?
- Is its predicate cheaper after neighboring operations are fused?
- Do measurement outcomes survive until correction and reverse execution?
- Does reset actually let allocation avoid the prior hard maximum ID?
- Is expected executed cost charged per outcome as assumed?
- Does the mechanism replace existing cleanup, or merely add a second one?

## Safe experiment ladder

1. Apply one-bit MBU to a Boolean with a tiny exact phase oracle.
2. Remove one correction deliberately and require a phase test to fail.
3. Apply the mechanism to a repeated carry or comparison boundary.
4. Test a small multi-bit register whose value is exactly recomputable.
5. Only then consider a 256-bit register or checkpoint.

For every level, test:

```text
basis values
superposition and relative phase
all measurement branches
ancilla and transcript cleanup
explicit forward followed by explicit reverse
average executed cost
hard-ID reduction
```

Stop scaling when reconstruction grows faster than the coherent state it
replaces or when physical allocation does not lower the peak.
