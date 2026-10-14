# Eight-paper mechanism matrix

## Comparison

| Paper | Unit of improvement | Main resource targeted | Most reusable mechanism | Direct-transfer barrier | Standalone KB expectation |
|---|---|---|---|---|---|
| Schrottenloher | inversion/multiplication architecture | both T and Q | compact history plus Bézout replay | different wrapper and approximate failure model | high |
| Litinski | controlled arithmetic and multiplication | T | controlled add-subtract | out-of-place result and Montgomery/QROM shell | medium |
| Luongo | garbage cleanup | expected T | phase-correct MBU | dynamic-circuit and inverse semantics | medium |
| Gidney | classical-constant addition | Q and T | vented carry plus dirty borrowing | current adders may already be at a local floor | high for local primitives |
| Spooky Pebbling | reversible schedule | Q for added time | ghost/checkpoint tradeoff | generic checkpointing already failed locally | medium as theory |
| Luo | full arithmetic architecture | Q | register sharing and demolition | literal circuit has very high T | medium for mechanisms, low literally |
| Khattar | EEA representation | state size / architecture | dialog and implicit division | polynomial-to-prime-field transfer | research-grade |
| Häner | integrated ECDLP circuit | end-to-end baseline | workspace reuse and scheduling | older and above the frontier | low as a direct win, high as control |

## Orthogonal dimensions

The set was chosen so that the primary questions differ:

```text
How should Euclid history be represented?       Schrottenloher
How can controlled arithmetic be cheaper?       Litinski
When can measurement replace uncomputation?     Luongo
How little workspace can constant addition use? Gidney
What are the schedule-level time/space limits?  Spooky Pebbling
How far can complete register sharing go?       Luo
Can quotient/dialog state replace explicit EEA? Khattar
What does a complete mature ECDLP stack look like? Häner
```

## Overlap that matters

### History and coefficient reconstruction

```text
Schrottenloher compact branch history
Luo explicit shared EEA state
Khattar quotient/dialog representation
current ping-pong sign tape and replay
```

These are alternatives for where the information needed to reconstruct coefficients lives. They cannot be combined by merely deleting one representation; every discarded bit needs an explicit recovery mechanism.

### Measurement and phase

```text
Luongo one-qubit MBU
Gidney carry venting
Luo full-register Hadamard demolition
Spooky ghosting
```

All exchange coherent quantum garbage for classical outcomes plus later phase repair. They differ in the form of the garbage and the cost of reconstructing its phase predicate.

### Arithmetic primitives

```text
Schrottenloher pseudo-Mersenne arithmetic
Litinski controlled add-subtract
Gidney constant adders
Häner Montgomery arithmetic
```

These are not plug-compatible. Choose according to modulus representation, whether operands are quantum or classical, control structure, output placement, and the phase where peak width occurs.

## Paper-specific nonclaims

- Schrottenloher does not prove its random-failure approximation passes all benchmark shots.
- Litinski does not supply a drop-in in-place prime-field multiplier for the current replay shell.
- Luongo does not make arbitrary multi-qubit garbage free to erase.
- Gidney does not guarantee improvement over a hand-specialized existing adder.
- Spooky Pebbling does not imply every checkpoint schedule beats direct replay.
- Luo's low qubit count does not imply a low score product.
- Khattar's polynomial EEA costs do not directly establish prime-field gains.
- Häner's mature baseline does not represent the 2026 frontier.
