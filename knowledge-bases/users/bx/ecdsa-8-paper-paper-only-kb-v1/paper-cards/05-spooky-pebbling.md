# Kornerup, Sadun, and Soloveichik: spooky pebbling

Source: arXiv:2110.08973v3, *Tight Bounds on the Spooky Pebble Game: Recycling
Qubits with Measurements*.

## Ghosting contract

**[EVIDENCE]** For computational-basis values `y_i` correlated with distinct
labels `x_i`, Hadamard-basis measurement can transform

```text
sum_i alpha_i |x_i>|y_i>
```

into

```text
sum_i alpha_i (-1)^(b dot y_i) |x_i>|0>,
```

where the classical string `b` records a phase obligation. The released
qubits may be reused for standard-basis computation. Removing the obligation
later requires recreating `y_i`, applying the `b`-controlled phase, and
uncomputing the recreation. See
[pages 4–5](../source-pages/spooky-2110.08973v3/page-04.md).

**[EVIDENCE]** Distinctness of the surviving labels is part of the definition
and prevents amplitudes from being merged irreversibly. Ghosting is therefore
not unrestricted erasure. See
[page 5](../source-pages/spooky-2110.08973v3/page-05.md).

**[EVIDENCE]** Classical measurement strings persist from ghosting until
unghosting. The method can reduce quantum workspace without reducing total
classical-plus-quantum memory. See
[page 6](../source-pages/spooky-2110.08973v3/page-06.md).

## Sequential-line tradeoff

**[EVIDENCE]** For a dependency line of length `n`, the paper gives a family
of strategies using `s` pebbles and `O(mn)` steps whenever

```text
n <= binomial(m+s-2, s-2) + 1.
```

It proves a matching asymptotic lower bound in the corresponding parameter
regime. See the overview on
[page 3](../source-pages/spooky-2110.08973v3/page-03.md), the construction on
[pages 8–11](../source-pages/spooky-2110.08973v3/page-08.md), and the lower
bound on
[pages 15–19](../source-pages/spooky-2110.08973v3/page-15.md).

**[EVIDENCE]** Representative regimes include three pebbles with quadratic
step count, logarithmically many pebbles with `O(n log n)` steps, and
`O(n^epsilon)` pebbles with `O(n/epsilon)` steps. See
[pages 2–3](../source-pages/spooky-2110.08973v3/page-02.md).

## General graphs and trees

**[EVIDENCE]** An irreversible pebbling with `s` pebbles and `T` steps can be
converted into a spooky pebbling using at most `s+1` pebbles and `O(nT)`
steps. For arbitrary directed acyclic graphs, approximating the minimum spooky
pebble number is PSPACE-hard. See
[page 20](../source-pages/spooky-2110.08973v3/page-20.md).

**[EVIDENCE]** A complete binary tree with `n=2^h-1` vertices has a strategy
using `h+1` pebbles and `O(n log n)` steps. See
[pages 21–22](../source-pages/spooky-2110.08973v3/page-21.md).

## Scope

**[EVIDENCE]** The pebble game counts abstract states and transitions. It does
not assign unequal widths or unequal recomputation costs to different
vertices. The paper's general-graph hardness result also rules out expecting a
single efficient optimum procedure for every dependency graph. See
[pages 20–23](../source-pages/spooky-2110.08973v3/page-20.md).
