---
kind: node
id: litinski-controlled-add-subtract
source: arXiv:2410.00899
---

# Controlled add-subtract

**[PAPER]** Implements:

```text
|c>|a>|b> -> |c>|a>|b+a>  if c=1
              |c>|a>|b-a>  if c=0
```

by complementing `a` around an ordinary ripple adder. Without carry-out, the cost is `n-1` Toffolis—the same as an uncontrolled adder and roughly half a controlled add-or-identity.

The saving is local; the unwanted subtract branch must be corrected globally.
