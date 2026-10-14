---
kind: node
id: failure-model
source: paper sections 1, 3, and 4
---

# Failure model

Approximation sources:

1. fixed Euclid iteration count is too short;
2. shrinking `u,v` slices are too narrow;
3. truncated `u>v` comparison is wrong;
4. modular overflow comparison is wrong;
5. adding `f` carries beyond the retained low slice;
6. the fast adder is used while `x+y=p` is still possible.

Paper validation:

```text
10,000 random-input successes
reported failure probability <= about 2^-13.3
```

The selected margins control empirical probability rather than providing a
worst-case correctness proof.

Related:

- [`paper-parameter-boundaries.md`](paper-parameter-boundaries.md)
- [`approximate-comparison.md`](approximate-comparison.md)
- [`x-plus-y-equals-p.md`](x-plus-y-equals-p.md)
- [`paper-interface-boundaries.md`](paper-interface-boundaries.md)
