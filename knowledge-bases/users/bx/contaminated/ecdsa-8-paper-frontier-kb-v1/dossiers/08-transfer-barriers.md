---
kind: research-dossier
id: transfer-barriers
depends_on: []
---

# Dossier: paper results require translation proofs

A paper mechanism is evidence that a construction exists under its own field,
interface, cost model, and cleanup semantics. It is not yet a benchmark
optimization.

## Translation card

Before implementation, fill:

```text
source field and residue representation
source input/output placement
source control type
source error or failure model
source measurement and inverse semantics
source resource metric
target interval and surrounding consumers
required conversion or bridge
```

## Eight principal barriers

| Paper | Attractive result | Required bridge |
|---|---|---|
| Schrottenloher | compact history, replay, pseudo-Mersenne arithmetic | exact benchmark wrapper and acceptance of all tested inputs |
| Litinski | cheaper controlled add-subtract and multiplication | absorb global corrections and fresh output placement |
| Luongo | half-expected garbage-oracle invocation | evaluator-compatible dynamic phase and explicit inverse |
| Gidney | constant-workspace classical-offset addition | prove the hot addend is classical and dirty halves are available |
| Spooky Pebbling | tight abstract time/qubit frontier | weighted nonuniform walk/replay/checkpoint model |
| Luo | three-field-register point-add architecture | avoid importing its literal high Toffoli cost; support demolition semantics |
| Khattar | compact Dialog and direct implicit division | construct integer prime-field transitions and sign recovery |
| Häner | mature integrated ECDLP scheduling | translate older arithmetic, wrapper, and T-resource model |

## Static benchmark barriers

**[BENCHMARK]**

- The offset coordinates are runtime classical bits, not a compile-time point
  table.
- All 9,024 deterministic circuit-seeded shots must pass.
- Every released non-output qubit and classical obligation must be clean.
- Relative phase and forward/reverse behavior are tested.
- Cost uses average executed Toffoli, not only emitted logical gates.
- Qubit cost is maximum referenced ID plus one, not an informal live count.
- A dynamic circuit requires an explicit reverse protocol.

## Common false transfers

```text
GF(2^b) XOR arithmetic -> secp256k1 integer arithmetic
fresh-output multiplier -> in-place replay without cleanup
expected paper count -> benchmark executed count without branch semantics
logical qubit count -> lower hard ID without allocator changes
random-input failure estimate -> exact acceptance on the fixed shot set
measurement and reset -> ordinary reversible gate-list reversal
unit-cost pebble step -> weighted arithmetic event
```

## Decisive experiment

Test the bridge, not the full paper:

- prime-field transition truth tables before a Dialog port;
- one complete corrected multiplier cell before replacing replay;
- one mutation-sensitive MBU gadget before field demolition;
- one allocator trace before implementing checkpoint recomputation.

If the bridge fails, retain the paper as a source of questions rather than
forcing its literal architecture into the benchmark.
