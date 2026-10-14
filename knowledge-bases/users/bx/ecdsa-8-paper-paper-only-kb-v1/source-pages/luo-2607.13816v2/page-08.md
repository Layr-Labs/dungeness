---
kind: source-page
source_id: arXiv:2607.13816v2
source_pdf: raw/2607.13816v2.pdf
source_page: 8
---

# Quantum Algorithm for Elliptic Curve Discrete Logarithms with Space-Efficient Point Addition - source page 8

The text below is a page-delimited extraction of the unchanged source PDF.

•Applications beyond elliptic-curve discrete logarithms.We note that modular inversion
is a general-purpose arithmetic primitive, not only restricted to ECDLP. It would be useful to
investigate whether the space-efficient reversible EEA and register-sharing techniques developed
here can improve other quantum algorithms that require modular division or inversion, such as
Decoded Quantum Interferometry (DQI) [KSG +25].
•AI-assisted discovery of quantum arithmetic circuits.An important open question is
whether AI systems can enable the automated design of quantum arithmetic circuits, support-
ing both the discovery of new resource-efficient circuits and the optimization of existing ones. One
possible approach is to encode techniques such as windowing, unary iteration, register sharing and
mid-circuit measurement as composable modules, and to develop AI-assisted evolutionary frame-
works, inspired by systems such as AlphaEvolve [NV+25] and SimpleTES [YLT+26], that iteratively
explore their replacement and composition under automated correctness verification and resource-
aware evaluation.
2 Preliminaries
This section provides a very brief discussion of the basic concepts used in this work. We assume that
readers have basic knowledge of quantum computation. For a general survey of quantum algorithms for
algebraic problems, we recommend the survey written by Childs and van Dam [CvD10].
2.1 Quantum computing and the Toffoli counts
We write basis quantum states as|x⟩, wherexis a bit string, and we model a quantum algorithm as a
circuit composed of elementary gates applied to one or more qubits. A key feature is that circuits can
create and transform superpositions of basis states, enabling interference effects that are exploited by
quantum algorithms.
At the fault-tolerant logical level, it is common to express circuits over a universal gate set such
as Clifford+T[NC10]. In many architectures theTgate is substantially more expensive than Clifford
operations, so circuit cost is frequently summarized byT-count,T-depth, or related metrics [FMMC12].
For design and validation, however, it is often convenient to use a purely reversible gate basis.
Accordingly, we express the main reversible components asToffoli networks. The Toffoli gate maps
|x, y, z⟩ 7−→ |x, y, z⊕(xy)⟩,
and it forms a universal primitive for classical reversible computation [NC10]. A practical benefit of
working at the Toffoli-network level is that such networks admit exact realizations over Clifford+T
[AMMR13], avoiding approximation overhead associated with synthesizing arbitrary unitaries. More-
over, Toffoli-based reversible circuits can be efficiently simulated on classical inputs at scales far beyond
what is possible for general quantum-state simulation, which makes testing and debugging large arith-
metic circuits significantly more tractable [HRS17]. For these reasons, we specify the core arithmetic and
elliptic-curve routines using Toffoli and CNOT gates.
8
