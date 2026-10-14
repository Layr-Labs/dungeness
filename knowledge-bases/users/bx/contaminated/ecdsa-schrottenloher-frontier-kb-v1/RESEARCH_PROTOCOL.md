# Protocol for deeper-than-paper research

## 1. State the residual bottleneck

After each valid improvement record:

```text
average executed Toffoli
hard maximum qubit ID
which phase owns each quantity
which live values overlap at the peak
which primitive repeats most often
```

## 2. Separate paper facts from degrees of freedom

A paper algorithm fixes a correct construction, not necessarily the cheapest
factorization under this evaluator. Mark every apparently fixed choice:

```text
state representation
round recurrence
branch alphabet
primitive boundaries
exactness boundary
cleanup method
operation schedule
```

## 3. Derive, then falsify

For a proposed transformation:

```text
write a small exact classical model
prove or exhaustively test its inverse
test exceptional zero and p relations
test phase repair by mutation
estimate complete-shell T and Q
only then integrate it
```

## 4. Use a portfolio

Do not spend the remaining run only tuning one scalar once a correctness cliff
has been found. Keep at least:

- one local arithmetic experiment;
- one representation experiment;
- one scheduling or lifetime experiment.

## 5. Measure continuation

The relevant research signal is not only final score. Also retain:

```text
score of first valid paper-derived candidate
best score after the paper architecture is complete
number of validated transformations after that point
score improvement after the last KB retrieval
budget remaining when the agent stops
```
