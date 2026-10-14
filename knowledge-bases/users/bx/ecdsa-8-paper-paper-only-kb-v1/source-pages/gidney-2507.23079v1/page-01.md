---
kind: source-page
source_id: arXiv:2507.23079v1
source_pdf: raw/2507.23079v1.pdf
source_page: 1
---

# A Classical-Quantum Adder with Constant Workspace and Linear Gates - source page 1

The text below is a page-delimited extraction of the unchanged source PDF.

A Classical-Quantum Adder with Constant
Workspace and Linear Gates
Craig Gidney
Google Quantum AI, Santa Barbara, California 93117, USA
August 1, 2025
In 2004, Cuccaro et al found a quantum-quantum adder withO(n) gate cost and
O(1) ancilla qubits. Since then, it’s been an open question whether classical-quantum
adders can achieve the same asymptotic complexity. These costs are particularly rele-
vanttomodulararithmeticcircuits, whichoftenoffsetbytheclassicallyknownmodulus.
In this paper, I construct an adder that uses 3 clean ancillae and4n±O(1) Toffoli
gates to add a classical offset into a quantum register. I also present an adder with a
Toffoli cost of3n±O(1) that uses 2 clean ancillae andn−2 dirty ancillae. I further
show that applying the presented adders conditioned on a control qubit requires no
additional workspace or Toffolis.
Data availability: Code and assets created for this paper are available on Zenodo [Gid25].
1 Introduction 1
2 Construction 2
2.1 Notation . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 2
2.2 Streaming Addition by Venting Carries . . . . . . . . . . . . . . . . . . . . . . . . . 3
2.3 Phasing by Carries . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
2.4 Borrowing Back and Forth . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
3 Conclusion 7
4 Acknowledgments 8
1 Introduction
The first quantum adder circuits neededΘ(n) gates andΘ(n) workspace qubits [VBE96]. In 2004,
Cuccaro et al found a way to eliminate the workspace, while preserving theΘ(n) gate count, by
temporarily moving carry information into the qubits of the offset register [Cuc+04]. However,
this can’t work for classical-quantum adders where the offset is stored in bits instead of qubits.
Extending the Cuccaro result to the classical-quantum case has remained an open problem since
2004.
There was some progress on the problem, between 2004 and now. In 2015, I found a solution
for the special case where the offset is 1 [Gid15]. In 2016, Häner et al found a divide-and-conquer
classical-quantum adder that used 1 dirty qubit andΘ(nlg n) gates [HRS17]. But reaching the
asymptotic limit ofΘ(n) gates remained unsolved.
In this paper I finally close the remaining asymptotic gap, achieving anΘ(n) gate count under
the constraint ofO(1) ancilla qubits. The new construction is based on three key ideas:
1. The ripple carry process of an addition can be streamed with constant workspace by eagerly
“venting” carry qubits (measuring them in the X basis as part of a measurement based
Craig Gidney: craig.gidney@gmail.com
1
arXiv:2507.23079v1  [quant-ph]  30 Jul 2025
