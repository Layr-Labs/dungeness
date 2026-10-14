# Unified eight-paper agent pack

Use this as a compact decision brief. It is not proof that any proposed circuit passes the benchmark.

## 1. Objective

```text
score = average executed Toffoli × (maximum referenced qubit id + 1)
```

Preserve affine correctness, clean released wires, zero residual phase, and explicit forward/reverse identity on all 9,024 benchmark shots.

## 2. Live architecture

**[BENCHMARK]** The current point-add path uses fixed-depth ping-pong division/multiplication:

```text
walk(u,v)
  -> one sign/history bit per round
  -> replay coefficients using the tape
  -> reverse walk
  -> clear tape and restore denominator
```

The tape/replay interval owns peak width. The exact round split and score are implementation state, not constants; inspect the current source and latest trusted run.

## 3. Eight mechanisms

### Schrottenloher — compact history and Bézout replay

Best architectural match. A fixed binary-Euclid walk records compact branch information and replays a linear transformation on a Bézout pair. Strongest transfers: history encoding, secp256k1 folds, truncated comparisons, and replay arithmetic. The paper wrapper and approximation model do not transfer unchanged.

### Litinski — controlled add-subtract and schoolbook arithmetic

The controlled add-subtract identity avoids paying for a fully controlled adder. It supports low leading-order multiplication counts. Main barrier: the multiplication is naturally out of place; a fresh accumulator can increase peak and erasing the input/result relation may require inversion-grade work.

### Luongo — measurement-based uncomputation

A one-qubit garbage function can be measured in the X basis: one branch needs no uncomputation and the other needs a phase repair. This gives expected, not deterministic, Toffoli savings. Transfer requires exact evaluator support for measurement, retained classical outcomes, phase correction, and explicit inversion.

### Gidney — constant-workspace classical adders

Carry information may be “vented” into phase and repaired through a cheaper carry-xor computation. Splitting a target lets each half borrow the other as dirty workspace. Strong candidate for constant/controlled arithmetic or a narrow peak interval; not automatically better than the current replay adder floor.

### Spooky Pebbling — time–space scheduling

Ghosting replaces a stored checkpoint with classical measurement information and later reconstruction. It gives rigorous tradeoffs, but generic Bennett-style checkpointing was already measured unfavorable in the current implementation. Use it to design schedule-specific replay interleaving, not as a generic instruction to checkpoint.

### Luo — low-space EEA and measured register recycling

Four-phase shared EEA state, active windows, unary iteration, and full-register Hadamard demolition reach 835 qubits for the paper point-add design but about 70.10M Toffolis. Literal transfer is too gate-heavy; liveness, dirty borrowing, and whole-register recycling are the valuable mechanisms.

### Khattar — explicit, implicit, and dialog EEA

Stores quotient information inside the evolving state and represents EEA evolution as small invertible transition matrices. Direct modular division can avoid materializing a full inverse. The paper's strongest results are for polynomial EEA over extension fields; prime-field integer transfer needs a new cost and information-recovery proof.

### Häner — integrated baseline

Montgomery multiplication, signed windowing, multiply-then-add pebbling, Kaliski inversion normalization, and workspace reuse form a mature end-to-end reference. Use it as a control and reconstruction guide, not as the expected frontier replacement.

## 4. Compatibility map

```text
current ping-pong walk/replay
  + Schrottenloher history/arithmetic ideas       high compatibility
  + Gidney constant/controlled adders             local compatibility
  + Luongo MBU                                    conditional on semantics
  + Luo register demolition/liveness              conditional on recovery
  + Spooky schedule theory                        schedule-specific only
  + Khattar dialog                                research transfer
  + Litinski multiplication                       component-only
  + Häner integrated architecture                 baseline/control
```

## 5. Ranked experiment sequence

1. Re-profile the exact peak interval and qubit-ID owner.
2. Compare current replay primitives with Schrottenloher's secp256k1-specific add/double/fold machinery.
3. Test Gidney-style constant or controlled addition only at an identified hotspot.
4. Build a tiny phase-sensitive Luongo-style MBU primitive; do not begin with a full register.
5. Interleave production and replay of history more aggressively, guided by Spooky scheduling but constrained by the measured checkpointing failures.
6. Prove whether discarded signs can be reconstructed before testing a Khattar-style implicit/dialog representation.
7. Test Luo-style whole-register demolition only when the old field value is exactly recomputable.
8. Use Litinski only if the surrounding shell absorbs the fresh accumulator and correction without increasing the peak.

## 6. Known traps

- Headline qubits multiplied by paper Toffolis are not benchmark scores.
- An out-of-place multiplier is not an in-place multiplier.
- Polynomial-field costs do not equal prime-field costs.
- Expected MBU cost is not a fixed gate count.
- Measurement cleanup without phase repair is incorrect.
- Saving live wires does not help if the highest referenced qubit ID remains.
- The sign/history tape stores information; it cannot simply be deleted.
- Generic checkpointing can lose on product even when it saves qubits.
- Approximation margins must pass every fixed benchmark shot.

## 7. Acceptance checklist

```text
same frozen base and harness
allowed files only
all 9,024 shots pass
no classical mismatch
no ancilla garbage
no phase garbage
forward/reverse identity
canonical score improves
experiment and failure recorded
```
