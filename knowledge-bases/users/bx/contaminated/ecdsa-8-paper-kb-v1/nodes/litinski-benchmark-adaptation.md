---
kind: node
id: litinski-benchmark-adaptation
source: cross-paper inference
depends_on: [litinski-controlled-add-subtract, litinski-prime-modular-multiplication]
---

# Litinski benchmark adaptation

**[INFERENCE]** Test in this order:

1. identify an existing controlled add where add/subtract semantics can be absorbed;
2. symbolically derive the correction in the current representation;
3. confirm corrections do not add a live 256-bit register at replay peak;
4. compare average executed Toffoli, not paper count;
5. only then model the full multiplier.

Stop if the fresh accumulator or its cleanup requires a second inversion-grade transformation.
