---
kind: research-dossier
id: space-is-a-schedule
depends_on: [history-information-channel, replay-linear-compiler]
---

# Dossier: peak space is a schedule, not a sum of headline registers

## Paper observation

**[PAPER]** Euclid operands shrink as history grows, so cleared high wires can
store later history symbols. Replay then consumes the history while maintaining
two modular values.

## Benchmark scoring consequence

**[BENCHMARK]** Qubit cost is the largest referenced qubit ID plus one. Fewer
conceptual live values do not help if allocation still touches the same high
ID.

## Build a round-indexed liveness model

For each round `i`, record:

```text
width of u and v
history prefix still needed
coefficient/replay widths
carry and comparison scratch
which wires can be physically reused
whether replay can execute before all history exists
```

## Scheduling questions

- Can history production and coefficient replay overlap?
- Can reverse reconstruction begin while multiplication replay is still active?
- Can the control symbol be consumed before the walk reaches maximum tape size?
- Can a low-space adder be used only at the global peak and a faster adder
  elsewhere?
- Can exact-prefix scratch be released before the bulk regime begins?

## Product break-even

For current executed Toffoli `T` and qubits `Q`, saving `dQ` qubits permits
approximately:

```text
added_T < T*dQ/(Q-dQ)
```

This must be evaluated at the complete-circuit level.

## Decisive experiment

Create an allocator-only or emitted-operation model parameterized by the
replay/walk split. Sweep the split and adder workspace cap before implementing
the full schedule. Verify the best predicted points with the trusted evaluator.
