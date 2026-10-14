# Gidney: vented carries and controlled classical offsets

Source: arXiv:2507.23079v1, *A Classical-Quantum Adder with Constant Workspace
and Linear Gates*.

## Operational role

This paper targets a particularly relevant primitive:

```text
quantum target <- quantum target + classically known offset
```

It obtains linear Toffoli cost with either constant clean workspace or a mix of
clean and dirty workspace. It also shows that the constructions can be
controlled without extra Toffolis.

For this benchmark, “classically known” must be interpreted carefully. A
runtime classical-bit register can often drive classically conditioned gates,
but it is not necessarily a compile-time literal. The implementation interface
must support the benchmark's form of classical control.

## Resource points

**[EVIDENCE]** The two main constructions are:

| Workspace | Toffoli | Other property |
|---|---:|---|
| 3 clean ancillas | `4n ± O(1)` | constant workspace |
| 2 clean + `n-2` dirty ancillas | `3n ± O(1)` | borrows a secondary register |

Both implement addition modulo `2^n`, have linear depth, and can be externally
controlled without additional workspace or Toffolis. See
[page 1](../../source-pages/gidney-2507.23079v1/page-01.md) and
[page 7](../../source-pages/gidney-2507.23079v1/page-07.md).

These are non-modular-by-prime adders. A prime-field wrapper still needs
comparison, correction, and clean flag handling.

## Carry venting

**[EVIDENCE]** Define the carry string as:

```text
carry(x,d,c0) = x xor d xor (x+d+c0)
```

The paper derives the identity:

```text
carry(~x', d, c0) = carry(x, d, c0)
where x' = x+d+c0
```

Thus a carry is a Z-basis function recoverable from values available after the
addition. Measuring a carry qubit in the X basis deletes its logical value. A
minus outcome leaves a phase task corresponding to that carry. The paper calls
this conversion from carry garbage to phase debt “venting.” See
[page 3](../../source-pages/gidney-2507.23079v1/page-03.md).

## Phase repair

**[EVIDENCE]** The phase tasks are repaired using a carry-XOR circuit:

```text
g <- g xor carry(target, d, c0)
```

Interleaving carry-XOR operations with classically controlled Z gates applies
the required phases while returning the dirty target `g` to its original
state. One carry-XOR is fused into the forward streaming addition; another is
used for repair. See pages
[3](../../source-pages/gidney-2507.23079v1/page-03.md)–[5](../../source-pages/gidney-2507.23079v1/page-05.md).

Unlike the one-bit Luongo lemma, this is a structured multi-bit deletion
protocol whose phase function is the carry process itself.

## Borrowing halves

**[EVIDENCE]** The constant-workspace construction splits the target into two
halves:

1. vent-add into the low half and retain the carry into the high half;
2. vent-add into the high half while borrowing the low half as dirty space;
3. repair high-half phases using the low half;
4. vent the cross-half carry;
5. repair low-half phases while borrowing the completed high half.

This yields the `4n ± O(1)` and three-clean-ancilla point. See
[page 7](../../source-pages/gidney-2507.23079v1/page-07.md).

## No-overhead outer control

**[EVIDENCE]** Offset bits only invert controls or control bit flips in the
construction. To control addition by an offset `d`, every literal `d_k=1` is
replaced by use of the external control and every `d_k=0` remains zero. This
introduces no additional Toffoli gates in the paper's gate accounting. See
pages [6](../../source-pages/gidney-2507.23079v1/page-06.md)–[7](../../source-pages/gidney-2507.23079v1/page-07.md).

## Transfer barriers and experiments

- **[EVIDENCE]** Scope is classical-quantum addition, not addition of two
  arbitrary quantum registers.
- **[EVIDENCE]** The dirty-ancilla variant must return all borrowed qubits
  exactly; overlapping them with live field values requires a lifetime proof.
- **[EVIDENCE]** Phase repair and measurement feed-forward are part of the
  primitive. Omitting them invalidates superposition behavior.
- **[INFERENCE]** Test this first for repeated additions of `p`, `2^32+977`,
  lookup-selected offsets, or reduction corrections controlled by runtime
  classical bits.
- **[INFERENCE]** Combine constant-workspace addition with the hard-ID
  scheduler: use the three-clean version at the Q peak and the dirty version
  where a dormant field register is available.
- **[INFERENCE]** Compare a prime-field modular wrapper built from this adder
  against Schrottenloher's truncated pseudo-Mersenne correction, including
  exact equality cases.
- **[INFERENCE]** The vented-carry representation suggests a more general
  design question: which transcript bits can be changed from stored Z-data
  into classically indexed phase obligations with cheap recomputation?
