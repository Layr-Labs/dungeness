---
kind: node
id: litinski-global-corrections
source: arXiv:2410.00899
depends_on: [litinski-controlled-add-subtract]
---

# Global correction terms

Each multiplier bit contributes either `+2^k y` or `-2^k y` plus a power-of-two offset. Summing all branches creates an affine expression in `x`, `y`, and `xy`.

**[PAPER]** A small number of full-width additions/subtractions and a final qubit relabeling divide the expression by two and recover `xy`.

**[INFERENCE]** A benchmark port wins only if these corrections fuse with operations already required by replay; otherwise the local adder saving may be consumed by global cleanup.
