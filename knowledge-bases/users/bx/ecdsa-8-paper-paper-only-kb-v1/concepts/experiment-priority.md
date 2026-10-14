# Source-only experiment priority

This ordering is based on dependency and falsifiability, not on any earlier
implementation outcome.

## Tier 1 — semantic micro-models

1. transcript construction and exact reverse;
2. transcript replay on arbitrary coefficient values;
3. one-bit measured cleanup with phase-sensitive tests;
4. vented-carry addition with explicit phase repair;
5. full-register demolition at small field widths.

## Tier 2 — complete primitive interfaces

6. clean fresh-output add-subtract multiplier;
7. in-place transcript multiplier;
8. exact shared-register EEA step;
9. Montgomery multiply–consume–uncompute shell.

## Tier 3 — cross-paper compositions

10. transcript core plus full-register demolition;
11. pseudo-Mersenne correction plus vented carries;
12. active-window lifetime proof with fixed-position arithmetic;
13. integer transition alphabet inspired by Dialog.

## Evidence required

Each experiment should report:

```text
mathematical interface
forward and inverse behavior
garbage and phase state
logical width
gate count in one declared model
source assumptions retained or changed
```
