---
title: Companion implementation map
source: gitlab.inria.fr/capsule/qarton-projects/ec-point-addition
revision: 9b23c9170a636a7097a02afb3a3d6cbb6425c9f4
tags: [source, code-map, qarton]
---

# Companion implementation map

**[CODE]** The paper's released implementation is a Python/Qarton reference, not a drop-in implementation for ecdsa.fail. It is still the best source for resolving underspecified constants, traversal order, backend choices, and exceptional cases.

## Top-level files

| File | Role |
|---|---|
| `build_circuit.py` | constructs point addition, reports resources, and launches random-input tests |
| `gcd_stats.py` | empirically estimates iteration and register-padding distributions |
| `point_add/point_add.py` | three-lookup affine point-add schedule |
| `point_add/gcd.py` | reversible history construction, Bézout replay, and in-place multiplication |
| `point_add/gcd_functions.py` | classical reference functions for history construction/replay |
| `point_add/compressor.py` | 6-bit valid-state to 5-bit compressor and inverse |
| `point_add/special_mod_arithmetic.py` | pseudo-Mersenne add, double, and square-add |
| `point_add/efficient_mod_arithmetic.py` | approximate generic-prime add, double, and square-add |
| `point_add/util.py` | measurement-based uncomputation wrapper |

## Class and function map

| Paper concept | Companion symbol |
|---|---|
| Euclid to history | `ToBitVector` |
| Classical Euclid reference | `to_bitvector` |
| Reverse history to original input | `from_bitvector` |
| Bézout/history replay | `ApplyBitVector` |
| Classical replay | `apply_bitvector` |
| Reverse replay | `apply_bitvector_reverse` |
| In-place modular multiplication | `IPModMul` |
| 3-step history compressor | `Compressor` |
| Read/write one symbol in compressed block | `Swapper`, `Absorber` |
| Pseudo-Mersenne doubling | `SpecialPrimeModularDouble` |
| Pseudo-Mersenne modular add | `SpecialPrimeControlledModularAdder` |
| Early-step `x+y=p`-safe add | `SpecialPrimeHandlePControlledModularAdder` |
| Controlled square-add | `ControlledSpecialPrimeModularSquareAdd` |
| Measurement uncomputation | `AutoMBU`, `AutoMBUInverse` |
| Full affine point addition | `WindowAffAddSpaceOpt` |

## Construction parameters

At the inspected July 22 revision:

```text
ITERATIONS_VAR = 2.4
U_PAD_VAR      = 2.3
TRUNCATE       = 40
ITER_CAN_BE_Q  = 50
PADDING        = 40
PADDING2       = 50
STEP           = 2
```

For `n=256`:

```text
iterations     = 402
compressed tape = 670 qubits
u/v pad         = 37 qubits
f               = 2^32 + 977
bit_length(f)   = 33
```

Thus a pseudo-Mersenne correction with padding 40 touches roughly the low 73 bits, and the square-add configuration with padding 50 touches roughly the low 83 bits.

## Traversal subtlety

The paper notes a convention-dependent result. The implementation resolves it:

- `ToBitVector(p)` maps `x` into the compressed Euclid record.
- `ApplyBitVector` reads the record from the final iteration back to the first.
- With `(y, 0)` as the replay pair, the implementation's selected direction yields `(0, x*y mod p)`.
- The inverse replay yields multiplication by `x^-1`.

Do not infer multiplication direction from a prose sentence alone. Verify it with a small classical model before wiring the reversible circuit.

## Exact structure of `IPModMul`

```text
input:  x, y
1. d = ToBitVector(x)              # x's storage becomes the history tape
2. allocate tmp = 0
3. ApplyBitVector(d, y, tmp)        # produces y=0, tmp=x*y
4. swap(y, tmp); release tmp
5. inverse(ToBitVector)(d)          # restore x
output: x, x*y
```

The important property is that history construction runs twice, while replay runs once. A conventional compute-inverse/use/uncompute design often pays for more full modular multiplications or coefficient storage.

## Backend selection

**History construction**

- An additional `n`-bit value is not simultaneously live, so more workspace is available.
- The implementation prefers a Gidney comparator and a controlled Gidney or hybrid adder.
- Space mode gives the hybrid adder the exact remaining ancilla budget.

**Replay**

- Replay is the peak-space region.
- Space mode selects CDKM-style controlled addition, low-space constant adders/comparators, and borrowed-bit MCX.
- Gate mode selects controlled Gidney addition/comparison and pays about `n` extra qubits.

**Square-add**

- Many ancillas are free outside the in-place multiplier.
- The implementation deliberately resets backend priority to aggressive Gidney primitives.

This phase-dependent backend choice is as important as the abstract algorithm.

## Approximation and failure sources

The source comments identify:

1. insufficient fixed Euclid iterations;
2. insufficient shrinking-register padding;
3. truncated Euclid comparisons;
4. truncated overflow comparisons in modular arithmetic;
5. limited carry propagation when adding `f`;
6. using the fast adder too early when a replay state can satisfy `x+y=p`.

The random-input simulator replaces exact arithmetic building blocks by classical functions but keeps approximate composite circuits live, so it tests these failure sources without simulating every gate.

## Version warning

The arXiv paper and the companion repository diverged after release. When reproducing the paper, use a matching historical commit. When solving the benchmark, the later code can be mined for additional optimizations, but label them as companion-code updates rather than paper-v1 results.
