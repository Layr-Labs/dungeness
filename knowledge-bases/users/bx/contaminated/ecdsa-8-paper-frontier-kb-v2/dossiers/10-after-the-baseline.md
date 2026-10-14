# Decision dossier: what to do after implementing a paper

A paper ends when it has established its claim. A benchmark research run should
continue because its objective, implementation constraints, and available
mechanism combinations differ from the paper's.

## A paper implementation is a new baseline

Immediately after a valid implementation:

```text
measure T
measure Q hard ID
locate T owner
locate Q owner
identify fixed assumptions inherited from the paper
mark which decision axes remain untouched
```

Do not spend the remaining budget merely making the code resemble the paper
more closely.

## Paper assumptions to reopen

For each implemented source, ask what it holds fixed:

### Schrottenloher

- fixed branch symbol encoding;
- probabilistic iteration/padding margins;
- one specific replay order;
- canonical pseudo-Mersenne representation;
- one point-addition output schedule.

### Litinski

- fresh output;
- Montgomery representation for prime modulus;
- schoolbook structure;
- global correction organization.

### Luongo

- one-bit MBU target;
- VBE/Takahashi modular-adder architecture;
- expected inverse-cleanup cost.

### Gidney

- classical offset;
- carry-based phase function;
- two workspace points;
- linear depth.

### Spooky Pebbling

- abstract uniform pebbles unless weighted by the implementation;
- line/tree/DAG schedule rather than arithmetic design.

### Luo

- exact four-phase recurrence;
- two-work-register shared layout;
- full-register demolition;
- space-first objective.

### Khattar

- polynomial fields;
- explicit/implicit Bézout use;
- transition-matrix alphabet.

### Häner

- Montgomery arithmetic portfolio available in 2020;
- Kaliski recurrence;
- affine coordinate choice;
- T/depth/width objectives rather than this product metric.

Each fixed assumption is a possible next direction.

## Forced frontier reset

Maintain an axis ledger:

```text
[ ] information medium
[ ] recurrence/state machine
[ ] control structure
[ ] field representation
[ ] output placement
[ ] measurement scale
[ ] lifetime schedule
[ ] cross-paper composition
[ ] allocator/hard-ID layout
[ ] exactness/failure budget
```

After an accepted improvement, do not choose the same box again until one
materially different box has been tested, unless profiling proves the same
owner still dominates by a large margin.

## Direction-generation loop

1. **Observe:** identify a measured owner or unexplained peak.
2. **Contrast:** find a paper with a different answer to that decision.
3. **Bridge:** write the interface and conversion.
4. **Predict:** estimate complete-shell `delta_T`, `delta_Q`, and failure mode.
5. **Falsify:** run the smallest test.
6. **Integrate:** only after the mechanism survives.
7. **Generalize:** record the reusable principle, not just tuned constants.
8. **Reset:** choose another axis.

This loop gives the agent a direction even when no paper states the next
complete architecture.

## Evidence budget

Allocate research effort roughly in this order:

```text
cheap owner measurement
cheap bridge derivation
small correctness experiment
representative resource measurement
complete integration
polish
```

Do not spend most of the budget surveying papers before a baseline or polishing
an unmeasured non-owner after it.

## When deeper research is real

An experiment counts as deeper research when it does at least one:

- creates a new representation of reversible information;
- proves or falsifies a cross-paper interface;
- moves computation across a lifetime boundary;
- changes output ABI and measures the complete caller;
- establishes a new exactness/resource tradeoff;
- derives a prime-field version of a mechanism previously limited to another
  field;
- records a general negative result with scope.

A long sequence of local constant tweaks inside the published architecture is
not necessarily deeper.

## Legitimate stopping conditions

Stop the run when:

- all remaining measured owners have only experiments whose optimistic product
  bound loses;
- materially different axes have decisive negative evidence;
- correctness cannot be preserved under the remaining bridge hypotheses;
- useful budget is insufficient for the smallest decisive test;
- repository or benchmark constraints block further authorized changes.

Do not stop because:

- the current paper's implementation is complete;
- one strong score has been found;
- a source's discussion section has no more suggestions;
- the latest experiment failed;
- the current mechanism has been locally optimized.

## Reusable discovery record

For every substantial result, write:

```text
principle
preconditions
forward contract
reverse/cleanup contract
resource effect
failure boundaries
tests
possible future callers
```

This is what allows a discovery to generalize to future runs instead of
remaining a one-off patch.
