# Decision dossier: space-time schedule and hard maximum ID

The benchmark's Q factor is the maximum referenced qubit ID plus one. This is
not identical to a paper's logical width, the sum of all named registers, or
the number of simultaneously nonzero qubits.

## First produce a lifetime trace

For every large register or workspace:

```text
allocation ID range
birth instruction
first use
last forward use
cleanup interval
free instruction
whether IDs are reused
whether measurement makes them reusable
value/function stored
cost to recompute
```

Mark the single instruction that establishes the high-water ID and list all
values that forced allocations below it.

## Scheduling mechanisms in the source set

### Shrink-and-grow sharing

Schrottenloher stores transcript bits in space released as Euclidean remainders
shrink. Luo overlays remainders, coefficients, quotient, and split values using
exact length metadata. Khattar overlays polynomial state with a growing
transition sequence.

The reusable principle is:

```text
prove complementary size invariant
define exact boundary metadata
restrict operations to active regions
show the inverse restores both values and boundaries
```

The proof, not physical overlap alone, creates valid sharing.

### Phase-specific arithmetic portfolios

Schrottenloher notes that forward/reverse GCD phases have about one register of
slack that disappears during replay. Use ancilla-rich low-T arithmetic only in
slack phases and low-workspace arithmetic at the width peak.

**[INFERENCE]** Select arithmetic per lifetime phase rather than one global
adder implementation.

### Active windows

Luo derives ranges that can be active at each global step and applies arithmetic
only there. This trades fewer wide operations for length controls, unary
iteration, and location-controlled gates.

Use active windows when a proven range is much smaller than `n` for a large
fraction of expensive steps. Measure control overhead at benchmark width.

### Lookup lifetime

Schrottenloher and Häner repeatedly load and unload selected point coordinates
instead of retaining two field registers through the entire point addition.
Lookup T can be cheaper than raising Q across inversion.

### Checkpoint/recompute

Spooky pebbling supplies schedules for replacing checkpoints with measurement
records and later replay. The theoretical line tradeoff is a starting point;
the actual circuit needs weighted nodes.

## Product-aware decision rule

For baseline `(T,Q)` and proposed `(T+dT,Q+dQ)`, compare:

```text
delta_score = (T+dT)(Q+dQ) - TQ
            = Q*dT + T*dQ + dT*dQ
```

A one-register reduction can justify substantial recomputation when `T` is
large, but only if it actually lowers the maximum referenced ID.

## Allocator experiments

1. Reorder only independent allocations so short-lived high-ID workspace is
   assigned below long-lived registers.
2. Reuse an exact dead ID range for the next workspace.
3. Move an ancilla-rich primitive out of the high-water interval.
4. Split one large operation into a low-workspace variant only at peak.
5. Recompute a selected lookup or temporary instead of retaining it.
6. Apply measurement demolition only if the freed range is reused before any
   higher ID appears.

Validate that ID reuse does not alias a value still needed by reverse
execution.

## Weighted checkpoint experiment

For a candidate chain, create:

| Node | Width freed | Forward T | Recompute T | Phase repair | Earliest delete | Latest restore |
|---|---:|---:|---:|---:|---|---|
| | | | | | | |

Enumerate a small number of checkpoint choices and compute the exact resulting
allocation peak. Do not optimize a proxy such as checkpoint count.

## Failure modes

- lowering logical width without lowering highest referenced ID;
- allocating a small late ancilla above all prior IDs;
- sharing registers whose values are needed by inverse calls;
- using dirty workspace without restoring unknown input;
- applying average shrinkage as a hard capacity bound;
- increasing dynamic calls in a region whose Q did not change;
- retaining lookup data through the inversion peak for a small T saving.

## Frontier hypotheses

- encode Euclid history into IDs released by both shrinking remainders and a
  temporarily dormant coordinate;
- use dirty Gidney addition in slack phases and three-clean addition at peak;
- demolish an old field register before transcript replay, then repair it after
  the transcript is gone;
- checkpoint only every `k` transition blocks and recompute local branch
  symbols;
- allocate classical-feed-forward ancillas in a reusable low-ID pool rather
  than monotonically extending the circuit.
