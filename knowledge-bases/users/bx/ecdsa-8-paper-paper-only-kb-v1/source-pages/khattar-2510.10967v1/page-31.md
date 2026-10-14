---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 31
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 31

The text below is a page-delimited extraction of the unchanged source PDF.

31
FIG. 4: Lattice Surgery diagram for compiling GF2 Multiplication (GF2Mul(10)) using Karatsuba algorithm by
stacking the Parity Control Toffoli primitive from Section VB. In Appendix C, we show how the Karatsuba
algorithm for GF2 multiplication can be viewed entirely as a sequence of Parity Control Toffoli gates. Forb = 10,
the we use the modified Karatsuba quantum circuit [9], which uses exactly45 (parity) Toffolis.
FIG. 5: Mockup of a physical layout for(m = 4095, n= 70, b= 12, r= 2016) OPI instance requiring1885 logical
qubits and5.72 × 106 Toffoli gates (see Table VI). The blue region stores logical qubits incold storage, where logical
qubits are stored as densely as possible but are not operated upon. The orange region stores logical qubits inhot
storage, where each logical qubit is stored “normally" using a surface code patch taking2 × (d + 1)2 physical qubits
and is actively operated upon. For a logical error rate (LER) of10−13, ad = 21 surface code with968 physical
qubits per logical qubit is used for hot storage and a 2D Yoked Surface Code [50] with350 physical qubits per
logical qubit is used for cold storage [20, Figure 6].
