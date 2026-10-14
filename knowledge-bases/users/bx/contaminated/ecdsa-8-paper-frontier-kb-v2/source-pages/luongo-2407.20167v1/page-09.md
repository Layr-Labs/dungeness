---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 9
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 9

The text below is a page-delimited extraction of the unchanged source PDF.

3. The central CNOT computes the second most significant bit of the sum, namely
Yn−1 ← sn−1 = xn−1 ⊕ yn−1 ⊕ cn−1 .
4. The last part of the circuit consists of a chain of n − 1 CARRY† and n SUM gates. Inverses of
the CARRY gate appear to restore every qubit of the temporary register C to its initial state
|0⟩. In particular, Ci ← 0 only after Bi ← ai ⊕ bi ⊕ ci.
CDKPM implementation A subsequent advancement over the VBE implementation was
proposed by Cuccaro, Draper, Kutin, and Petrie Moulton (CDKPM) in [Cuc+04]. Their strategy
greatly improves the use of ancillary qubits, requiring only one ancilla in contrast to the linearly
many qubits required by the VBE adder. Moreover, this circuit enjoys a smaller depth, uses fewer
gates and requires less space. The CDKPM implementation is based on the two auxiliary gates
MAJ (majority) and UMA(unmajority and add). The MAJ gate is given in figure 6; it computes the
majority function of three bits in place (See equation (5) in section 1.3), while the UMA, given in
figure 7 gate, restores the original values and writes the sum to the output as shown in figure 9.
M
A
J =
Figure 6: Majority gate ( MAJ) as described in Cuccaro et al. [Cuc+04] The MAJ gate performs the mapping
|ck, yk, xk⟩ 7→ |ck ⊕ xk, yk ⊕ xk, maj(xk, yk, ck)⟩ where the function maj is defined in equation (5).
U
M
A =
U
M
A =
Figure 7: Unmajority gate (2 CNOT version and 3 CNOT version) as described in Cuccaro et al. [Cuc+04]. The UMA
gate performs the mapping |xi, yi, ci⟩ 7→ |ai ⊕ ci ⊕ xiyi, xi ⊕ yi ⊕ ci ⊕ xiyi, ci ⊕ xiyi⟩. The operator is not self-adjoint,
(UMA)† performs the mapping |ck, yk, xk⟩ 7→ |ck ⊕ xk, ck ⊕ yk, maj(xk, yk ⊕ 1, ck)⟩.
Proposition 2.3 (CDKPM plain adder [Cuc+04]) . There is a circuit implementing an n-bit
quantum addition as per definition 2.1 using 1 ancilla qubit and 2n Tof gates.
Proof. The sought circuit is given in figure 8. The first qubit C0 is an ancilla prepared in the state
c0 = 0, and the last qubit Yn is the extra qubit meant to take into account the possible sum overflow.
The circuit consists of a sequence of n MAJ gates, a central CNOT copying the most significant
carry in the register Yn and a final sequence of UMA gates. The combination of MAJ and UMA
gates is shown in figure 9.
Gidney implementation A variant of the CDKPM adder was proposed by Gidney [Gid18]
(shown in figure 13). The implementation involves replacing Tof gates in the MAJ blocks by a
temporary logical-AND stored in an ancilla qubit. This increases the number of ancillas by n: one
9
