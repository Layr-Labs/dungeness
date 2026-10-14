---
kind: node
id: x-plus-y-equals-p
source: paper section 4, Algorithm 11
depends_on: [pseudo-mersenne-controlled-addition]
---

# Exceptional case: x+y=p

During the first empty iterations of Bézout replay, inputs can satisfy:

```text
x+y=p
```

This is negligible for uniform independent inputs but structurally present here.

The special adder:

1. detects the high-bit all-ones pattern;
2. maps the `p` representation to zero with controlled XOR;
3. folds ordinary overflow with `f`;
4. erases flags using the zero high-bit pattern and a comparison.

Companion code uses this variant for the first:

```text
ITER_CAN_BE_Q = 50
```

replay iterations, then switches to the faster ordinary pseudo-Mersenne adder.
