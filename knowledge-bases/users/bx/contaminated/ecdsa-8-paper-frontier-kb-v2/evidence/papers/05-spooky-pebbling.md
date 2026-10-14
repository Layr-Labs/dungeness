# Kornerup–Sadun–Soloveichik: spooky pebbling and qubit recycling

Source: arXiv:2110.08973v3, *Tight Bounds on the Spooky Pebble Game: Recycling
Qubits with Measurements*.

## Operational role

This paper supplies a global scheduling language for measurement-assisted
recycling. It does not give an ECDSA arithmetic circuit. It explains when
intermediate values can be replaced by classical measurement records and phase
obligations, then recomputed later.

Its strongest use here is to challenge an existing lifetime schedule after the
arithmetic data-dependency graph has been measured.

## Ghosting contract

**[EVIDENCE]** A register containing `y_i` correlated with distinct `x_i` can
be ghosted:

```text
sum_i alpha_i |x_i>|y_i>
  ->
sum_i alpha_i (-1)^(b dot y_i) |x_i>|0>
```

where `b` is a retained classical measurement string. The qubits are available
for later standard-basis work, but the phase obligation must be removed before
incompatible basis use. Removal requires recreating the old value, applying
the `b`-controlled phase correction, and uncomputing it. See pages
[4](../../source-pages/spooky-2110.08973v3/page-04.md)–[5](../../source-pages/spooky-2110.08973v3/page-05.md).

**[EVIDENCE]** The distinct-`x_i` condition is part of the definition; it
prevents destructive merging of amplitudes. Ghosting is not arbitrary
irreversible erasure. See [page 5](../../source-pages/spooky-2110.08973v3/page-05.md).

**[EVIDENCE]** Classical records remain live from ghosting to unghosting, so
the method reduces qubits but not total classical-plus-quantum memory. See
[page 6](../../source-pages/spooky-2110.08973v3/page-06.md).

## Line tradeoff

**[EVIDENCE]** For a sequential dependency line of length `n`, the paper gives
a family of spooky-pebbling strategies using `s` pebbles and `O(mn)` steps
when:

```text
n <= binomial(m+s-2, s-2) + 1
```

and proves a matching asymptotic lower bound in the corresponding regime. See
the result overview on [page 3](../../source-pages/spooky-2110.08973v3/page-03.md),
the construction around pages
[8](../../source-pages/spooky-2110.08973v3/page-08.md)–[11](../../source-pages/spooky-2110.08973v3/page-11.md),
and the lower-bound development on pages
[15](../../source-pages/spooky-2110.08973v3/page-15.md)–[19](../../source-pages/spooky-2110.08973v3/page-19.md).

The binomial relationship is more useful than a vague “trade time for space”
claim: it can generate concrete checkpoint counts for a measured chain.

## General graphs

**[EVIDENCE]** An irreversible pebbling using `s` pebbles and `T` steps can be
converted to a spooky pebbling using at most `s+1` pebbles and `O(nT)` steps.
For arbitrary DAGs, even approximating the minimum spooky pebble number is
PSPACE-hard. See
[page 20](../../source-pages/spooky-2110.08973v3/page-20.md).

**[EVIDENCE]** For a complete binary tree with `n=2^h-1`, the paper gives an
`h+1` pebble, `O(n log n)` strategy. See pages
[21](../../source-pages/spooky-2110.08973v3/page-21.md)–[22](../../source-pages/spooky-2110.08973v3/page-22.md).

These results warn against assuming one universal checkpoint schedule. The
shape and weights of the actual arithmetic DAG matter.

## Benchmark translation

One pebble in the theory corresponds to an entire word/state block. In the
benchmark, blocks have unequal widths and recomputation costs. A practical
translation must use a weighted schedule:

```text
node weight_Q = qubits made reusable
edge/subgraph weight_T = expected recomputation Toffoli
eligibility = standard-basis reuse + recoverable phase + distinct labels
hard-ID effect = whether recycling changes the highest allocation interval
```

## Transfer barriers and experiments

- **[EVIDENCE]** Ghosted qubits may be reused for standard-basis computation;
  arbitrary basis changes before unghosting are unsafe.
- **[EVIDENCE]** Classical measurement strings are obligations, not disposable
  logging.
- **[INFERENCE]** Extract the actual point-addition call DAG and annotate every
  large temporary with birth, last forward use, recomputation root, and phase
  eligibility.
- **[INFERENCE]** First test one heavy chain, such as inversion history or a
  multiply–correct–uncompute sequence, rather than solving the full DAG.
- **[INFERENCE]** Optimize for the benchmark's hard maximum ID, not minimum
  simultaneous logical width alone. Recycling a register below the current
  high-water mark may not change Q.
- **[INFERENCE]** Combine spooky scheduling with Schrottenloher's phase-specific
  slack: expensive recomputation may be acceptable if it removes a register
  exactly at replay's width peak.
