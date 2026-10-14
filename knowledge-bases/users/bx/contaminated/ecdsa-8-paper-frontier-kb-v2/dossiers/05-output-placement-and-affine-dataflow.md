# Decision dossier: output placement and affine dataflow

The placement of a result determines which inputs coexist, whether a producer
must be reversed, and which register establishes the hard maximum ID. “In
place” and “out of place” are architectural decisions, not cosmetic APIs.

## Output ABIs in the source set

| ABI | Source | Strength | Cost hidden by local primitive count |
|---|---|---|---|
| `|x>|y> -> |x>|xy>` | [Schrottenloher](../evidence/papers/01-schrottenloher.md) | no fresh product register | transcript plus replay |
| `|x>|y>|0> -> |x>|y>|xy>` | [Litinski](../evidence/papers/02-litinski.md) | cheap schoolbook body, natural square/product | result, garbage, copy/uncompute |
| compute temporary then consume before reverse | [Häner](../evidence/papers/08-haner.md) | avoids copy or second forward compute | consumer must fit producer lifetime |
| compute fresh result, measure old register, repair phase, swap | [Luo](../evidence/papers/06-luo.md) | emulates in-place map with three field registers | recomputation and feed-forward |

## Draw the affine shell as values, not subroutine names

For one point addition, make a table:

| Time | X register | Y register | temporary A | other large state | last use |
|---|---|---|---|---|---|
| initial | target x | target y | clean? | | |
| differences | | | | | |
| division | | | | | |
| square/correction | | | | | |
| multiply | | | | | |
| final correction | output x | output y | clean | | |

Then annotate the highest referenced ID at every phase. The register count
alone does not reveal the benchmark Q factor.

## Producer-consumer fusion

Häner's multiply-then-add and square-then-subtract examples retain a produced
temporary through its sole consumer, then reverse the producer. This can:

- replace a copy with the consumer operation;
- avoid computing the same temporary twice;
- remove a dedicated result register if a consumer target already exists.

**[INFERENCE]** Search the benchmark for:

```text
produce z into clean register
use z exactly once in add/subtract
copy or move z
reverse producer
```

Replace the copy/move with the actual consumer when algebra permits.

## Fresh-output versus in-place multiplication

Litinski's multiplier may reduce Toffoli but requires a fresh accumulator and
may require a second clean result during uncomputation. Schrottenloher's replay
keeps output in the original `y` register but retains a large transcript.

Compare at complete-call scope:

```text
fresh:
  forward multiplier
  result accumulator
  garbage
  copy/consume
  reverse multiplier

in-place:
  build transformation record
  replay on target
  restore transformation input
```

The cheaper ABI depends on whether a dormant field register or transcript space
already exists at the call site.

## Demolition as ABI conversion

Luo converts a fresh-output multiplier/divider into an in-place interface:

```text
fresh result in A
Hadamard-measure old Y
reuse Y to clean producer state
recreate old Y
repair measurement phase
uncompute recreation
swap A into Y
```

This does not erase information for free. It moves old-`Y` information into a
classical phase key and later pays to recompute it.

**[INFERENCE]** The wrapper can be studied independently of Luo's EEA. Apply
it to the cheapest available fresh-output multiplier and measure whether its
three-register lifetime beats an in-place transcript design.

## Offset lookup lifetime

Schrottenloher loads selected coordinates at each of three use sites and
unloads them immediately. Häner similarly observes that repeated lookups can
fit into otherwise idle workspace, trading lookup T for lower width.

For runtime-classical offsets, test:

- retain both coordinates throughout;
- load each coordinate at each use;
- retain only one coordinate;
- recompute a derived value such as `3x`;
- place lookup workspace in an interval below the hard-ID owner.

## Experiments

1. Generate a value-lifetime trace for the current affine shell.
2. Identify the exact allocation that establishes maximum ID.
3. Test one producer-consumer fusion without changing arithmetic.
4. Test one alternative multiplication ABI behind a common wrapper.
5. Include reverse execution and measurement repair.
6. Recompute both average Toffoli and maximum ID after allocator changes.

## Rejection criteria

Reject a local ABI win if conversion, copy/uncompute, or extended lifetime
dominates it. Record the caller where it might still become useful; output
placement is context-dependent.
