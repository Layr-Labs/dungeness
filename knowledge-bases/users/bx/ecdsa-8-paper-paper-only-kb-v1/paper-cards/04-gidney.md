# Gidney: carry venting and constant-workspace addition

Source: arXiv:2507.23079v1, *A Classical-Quantum Adder with Constant Workspace
and Linear Gates*.

## Resource points

**[EVIDENCE]** The paper gives two classical-quantum adders modulo `2^n`:

| Workspace | Toffolis | Depth |
|---|---:|---:|
| 3 clean ancillas | `4n ± O(1)` | linear |
| 2 clean plus `n-2` dirty ancillas | `3n ± O(1)` | linear |

Both constructions can be externally controlled without additional workspace
or Toffolis in the paper's accounting. See
[pages 1 and 7](../source-pages/gidney-2507.23079v1/page-01.md).

## Carry venting

**[EVIDENCE]** The carry string satisfies

```text
carry(x,d,c0) = x xor d xor (x+d+c0)
```

and the paper derives

```text
carry(~x',d,c0) = carry(x,d,c0),
where x' = x+d+c0.
```

Consequently, a carry is recoverable from values available after addition.
Measuring its qubit in the X basis frees the qubit but can leave a phase
obligation. The paper calls this conversion from stored carry data to deferred
phase work “venting.” See
[page 3](../source-pages/gidney-2507.23079v1/page-03.md).

## Carry-XOR phase repair

**[EVIDENCE]** Deferred phases are repaired with a circuit of the form

```text
g <- g xor carry(target,d,c0).
```

Carry-XOR operations are interleaved with classically controlled phase gates
while the borrowed register `g` is returned to its original value. See
[pages 3–5](../source-pages/gidney-2507.23079v1/page-03.md).

## Borrowing target halves

**[EVIDENCE]** The three-clean-ancilla construction splits the target into two
halves. It updates one half while borrowing the other as dirty workspace,
repairs the corresponding phases, then exchanges the roles of the halves. A
separate cross-half carry is vented and repaired. See
[page 7](../source-pages/gidney-2507.23079v1/page-07.md).

## External control

**[EVIDENCE]** Offset bits enter the construction as inversions of controls or
as classically selected bit flips. To add the offset conditionally, literals
equal to one are replaced by use of an external control, while zero literals
remain inactive. The paper's circuit therefore adds that outer control without
extra Toffolis. See
[pages 6–7](../source-pages/gidney-2507.23079v1/page-06.md).

## Scope

**[EVIDENCE]** These circuits add a classically specified offset to a quantum
target modulo `2^n`; they are not arbitrary quantum-quantum adders or complete
prime-field modular adders. Borrowed qubits must be restored exactly, and the
measurement outcomes and phase-repair operations are part of the primitive.
See [pages 1–7](../source-pages/gidney-2507.23079v1/page-01.md).
