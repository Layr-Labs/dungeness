---
kind: source-page
source_id: arXiv:2507.23079v1
source_pdf: raw/2507.23079v1.pdf
source_page: 5
---

# A Classical-Quantum Adder with Constant Workspace and Linear Gates - source page 5

The text below is a page-delimited extraction of the unchanged source PDF.

Figure 4: Ann = 6example of an adder that uses 2 clean ancillae,n −2 dirty ancillae, and3n ±O(1) Toffolis.
Top: decomposed into other subroutines defined by the paper. Bottom: further decomposed into constant sized
gates. Performs target →(target+ d + carryin) mod 2n. The circuit ends with an instance of the carry-xor
from Figure 3, conjugated by classically-controlled Z gates to correct the phase vented by the streaming adder
from Figure 2 at the start of the circuit. Note that the streaming adder is tweaked to xor carries into the dirty
qubits as it runs, saving one instance of the expensive carry-xor construction.
5
