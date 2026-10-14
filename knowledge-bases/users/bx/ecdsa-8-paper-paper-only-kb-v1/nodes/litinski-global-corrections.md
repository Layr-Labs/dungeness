---
kind: node
id: litinski-global-corrections
source: arXiv:2410.00899
depends_on: [litinski-controlled-add-subtract]
---

# Global correction terms

Each multiplier bit contributes either `+2^k y` or `-2^k y` plus a power-of-two offset. Summing all branches creates an affine expression in `x`, `y`, and `xy`.

**[PAPER]** A small number of full-width additions/subtractions and a final qubit relabeling divide the expression by two and recover `xy`.

**[SYNTHESIS]** The controlled add-subtract saving must be evaluated together
with these global corrections; replacing one isolated controlled addition does
not realize the paper's multiplication count.
