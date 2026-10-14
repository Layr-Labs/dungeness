---
kind: node
id: approximate-comparison
source: paper section 4
---

# Approximate comparison

Replace an `n`-bit comparison by a comparison of the most significant `k` bits, typically 40-50.

Used for:

- Euclid branch choice `u>v`;
- deciding whether an addition crossed `p`;
- erasing a reduction flag using `result<addend`.

Benefit: comparison cost scales with `k`, not `n`.

Failure condition: compared values differ only below the retained high-bit window.

The retained width is a paper-level error parameter rather than a universal
constant.

Risk model: [`failure-model.md`](failure-model.md).
