---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 5
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 5

The text below is a page-delimited extraction of the unchanged source PDF.

•
b∈{0,1}
•
|x⟩
Uf Uf
|x⟩
|f(x)⟩ H
(−1)bf(x) |x⟩|0⟩
Z |0⟩
Figure 2: Circuit to ghost f(x) and later correct the phase in order to overall uncomputef(x) using
measurement-based uncomputing, as described in [11].
b∈{0,1}
•
|x⟩
Ef Uf
|x⟩
|f(x)⟩ G
(−1)bf(x) |x⟩|0⟩
|0⟩
Figure 3: The circuit from Figure 2 using G andEf circuit macros. Note that the•on the classical wire above
the Ef gate represents a controlled application of the componentZ gate rather than a controlled application
of an entire module.
Since the logical value of the register has been zeroed out, it can be used as if it were a fresh
ancilla register for any subsequent computation acting only in the standard basis. However for a
quantum circuit to behave correctly, this ghost must be removed before acting on this register in
another basis. By recreating the state of theyregister as it was before ghosting and recalling the
classical bitstringb, the ghost can be removed by applying ab-controlled Z gate to the register.
Finally uncomputation can be used to properly uncompute the register. While this might seem
like uncomputation with extra steps, we will see thatreusing registers before we could uncompute
their values allows for more qubit and gate efficient quantum algorithms.
Ghosting is not a unitary operation and thus requires intermediate measurements: for ex-
ample, if you tried to ghost the second qubit in the state(|00⟩+ |01⟩)/
√
2 and receive b = 0,
then you would end up with the non-normalized state(|00⟩+ |00⟩)/
√
2 =
√
2 |00⟩. Importantly,
note that ghosting is only defined to perform this mapping when thexi are distinct, as that is
sufficient to prevent interference between basis states and make it a norm-preserving operation.
In [11] Gidney shows that ghosting can be performed by measuring in the Hadamard basis,
recording the result as classical outputb, and then usingb to apply a controlledX-gate to the
register. Figure 2 shows what this circuit looks like, as the gates on the left “ghost” thef(x)
register and the gates on the right recomputef(x) before removing the ghost and uncomputing
f(x). Importantly, the gates that ghost thef(x) register do not use thex register, so these
operations can be performed even when thex register is holding a different value. However,
removing the ghost then requires the presence ofx.
For compactness, we compress the highlighted gates on the left and the right of Figure 2
into single gatesG and Ef as shown in Figure 3. When performing a classical subroutine on a
quantum computer, theG gate can be applied to any register at any time to reset the logical
value of its qubits (ghosting). However, whenever this is done, theEf gate must be reapplied
later in the circuit when it is possible to recompute the original value in the erased register and
remove the phase (unghosting).
5
