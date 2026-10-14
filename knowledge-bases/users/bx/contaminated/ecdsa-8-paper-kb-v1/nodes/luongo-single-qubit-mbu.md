---
kind: node
id: luongo-single-qubit-mbu
source: arXiv:2407.20167, MBU lemma
---

# Single-qubit MBU lemma

Given a self-adjoint oracle:

```text
Ug |x>|b> = |x>|b xor g(x)>
```

measure the garbage qubit in the X basis. One outcome deletes it cleanly. The other leaves phase `(-1)^g(x)` and calls `Ug` inside a phase-repair gadget.

**[PAPER]** The expensive oracle is used with probability `1/2`.

This is phase-correct deletion, not ordinary reset.
