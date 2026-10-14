---
kind: node
id: implementation-parameters
source: companion code revision 9b23c917
---

# Implementation parameters

Released code constants:

```text
ITERATIONS_VAR = 2.4
U_PAD_VAR      = 2.3
TRUNCATE       = 40
ITER_CAN_BE_Q  = 50
PADDING        = 40
PADDING2       = 50
STEP           = 2
```

At `n=256`:

```text
iterations = 402
u/v padding = 37
tape bits = 670
```

Meaning:

- `ITERATIONS_VAR`: tail slack in fixed Euclid length;
- `U_PAD_VAR`: high-bit slack in shrinking `u,v`;
- `TRUNCATE`: Euclid comparison window;
- `ITER_CAN_BE_Q`: replay prefix using equality-safe modular add;
- `PADDING`: carry/comparison margin in replay arithmetic;
- `PADDING2`: margin in square-add;
- `STEP`: width-rounding granularity during circuit construction.

All are engineering choices tied to an empirical failure target.
