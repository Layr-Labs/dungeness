# Protocol for cross-paper research

## 1. Establish the measured base

Record:

```text
validity status
average executed Toffoli
hard maximum qubit ID
phase that owns each quantity
repeated hot primitive
values live at the hard-ID peak
```

Do not let a paper-reported resource table replace this profile.

## 2. Select a decision, not a paper

Choose one frontier axis and name the competing answers. For example:

```text
branch tape vs explicit EEA state vs dialog vs classical ghost
quantum-controlled add vs add/subtract vs controlled constant add
coherent cleanup vs one-bit MBU vs field-register demolition
```

## 3. Write the bridge lemma

Every cross-paper proposal needs a short claim of the form:

```text
Given surviving state S, source mechanism M can replace target interval I
because discarded information D can be recovered by R, while preserving field
representation F and explicit inverse protocol V.
```

List the weakest assumption whose failure would refute the claim.

## 4. Derive before integrating

Use the smallest model that contains the disputed property:

- exhaustive small-width state transitions for recurrence and history;
- symbolic affine expressions for correction fusion;
- exact bounded-residue models for reduction;
- mutation-sensitive phase tests for measurement;
- interval and allocator simulation for schedule changes.

Only integrate after the bridge survives its local falsifier.

## 5. Cost the closed shell

Include:

```text
preparation
central primitive
global corrections
cleanup
phase repair
representation conversion
explicit inverse
hard-ID effect
```

Headline primitive counts are insufficient.

For base `(T,Q)` and candidate deltas `(dT,dQ)`, require:

```text
(T+dT)(Q+dQ) < TQ
```

## 6. Maintain a three-axis portfolio

After the first strong valid candidate, keep at least:

- one representation or state-machine hypothesis;
- one algebra or arithmetic hypothesis;
- one schedule, lifetime, or measurement hypothesis.

Reject branches decisively rather than tuning all of them indefinitely.

## 7. Reset the frontier after every strong result

Ask:

```text
Did the result change only a parameter?
Which architectural choice is now the owner?
Which paper supplies a genuinely different answer to that choice?
What transfer barrier has not yet been tested?
```

## 8. Measure research continuation

Useful trajectory signals are:

```text
score of first valid baseline
best score after one paper spine is complete
number of bridge hypotheses tested after that point
number of cross-paper transformations validated
last improvement after a frontier retrieval
budget remaining when work stops
```

Stopping because one paper reaches its conclusion is not evidence that the
design space has been exhausted.
