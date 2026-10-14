---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 12
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 12

The text below is a page-delimited extraction of the unchanged source PDF.

struction method from [14] is also more efficient because only Algorithm 2 is run
twice.
We can now use Algorithm 2 and Algorithm 3 to implement in-place modular
multiplication. On input (x, y), we have three steps:
–We convertxinto a garbage bit-vectorgrepresenting the EEA operations;
–We usegto mapyintoxymodq;
–We convertgback tox.
The algorithm is Algorithm 4.
Algorithm 4In-place modular multiplication.
Input:Registersx, y
1:Output:Registers containx, yxmodq
2: Convertxto bit-vectorgusing Algorithm 2
▷Registers are nowg, y
3: Use the B´ ezout reconstruction algorithm Algorithm 3 on (y,0)
▷Registers are nowg, yxmodq
4: Convert backgtox
▷Registers are nowx, yxmodq
We can make a few observations:
–The space complexity of the entire point addition circuit depends on Al-
gorithm 4 only. All other steps can be implemented using space-efficient
components, or sometimes using some trade-offs. For example, ancillas are
available during the modular squaring.
–If space-efficient components are used for arithmetic operations, then the
dominating step in space complexity is the B´ ezout reconstruction step. At
this point, we need to store 2nbits for the two input registers, as well as the
bit-vector representation of size 2.355n+O( √n). This gives a total space
complexity of 4.355n+O( √n).
–The GCD construction (Algorithm 2), both forwards and backwards, uses
only 2.355n+O( √n) qubits in total. With the additional register ofnbits
stored at this point, this means that aroundnqubits are available for trade-
offs. In particular, we can use more gate-efficient arithmetic circuit like Gid-
ney’s adder [7], which we cannot use during the reconstruction.
–If we still use gate-efficient arithmetic during the reconstruction step, then
we will neednadditional ancilla qubits, but we will save a few Toffoli gates.
This is precisely the difference between the two variants of the Babbush et
al.’s circuits [2] as well as ours.
4 Approximate Arithmetic and Modular Arithmetic
At this point, we will obtain a circuit with roughly the same qubit count as [2]
(a bit higher), but a larger gate count. We then optimize the arithmetic com-
12
