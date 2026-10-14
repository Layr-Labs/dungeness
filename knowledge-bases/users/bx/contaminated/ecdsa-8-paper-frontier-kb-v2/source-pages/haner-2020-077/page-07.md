---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 7
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 7

The text below is a page-delimited extraction of the unchanged source PDF.

|x0⟩
|x1⟩...
|xk⟩
|y⟩
|0⟩
|0⟩...
|0⟩...
|0⟩
|0⟩...
|0⟩
|0⟩
|0⟩
n
k
n+k
+
+
+
+
···
···
···
···
···
···
···
···
···
···
···
···
+
+
cpy Inmi
T[mi] +
+
Inmi
T[mi]
/2k
|x0⟩
|x1⟩...
|xk⟩
|y⟩
|(xy)0⟩
|(xy)1⟩...
|(xy)k⟩...
|(xy)n⟩
|0⟩...
|0⟩
|mi⟩
|0⟩
Fig. 4: Circuit for a single window of windowed add-and-halve multiplication. The cpy gate copies
k bits with k CNOT gates. The gate Inmi performs a quantum table look-up of T[mi], where T
is the table described in the text. The circuit in this ﬁgure is repeated ⌈n/k⌉times, with a ﬁnal
modular correction step, to perform a single modular multiplication.
Pebbling. Given integers x, y, and z, one method to compute xy+ z in place is to ﬁrst compute
xy in an auxiliary register, then to add it to the register containing z, and ﬁnally to uncompute xy.
This works for any generic multiplication circuit, but at the cost of two multiplications.
The circuit we use requires the Bennett method, and we replace its CNOT step with an addition.
This is just a pebbling technique [ 5]; we are keeping the auxiliary qubits until we have ﬁnished
the next computation (an addition) before uncomputing them. The cost of this multiply-then-add
is just the sum of the costs of a multiplication and an addition, rather than twice the cost of a
multiplication and an addition.
In particular, RNSL treat their squaring circuit as a black box in the full elliptic curve addition
circuit. The computed square is only needed for one subtraction before it must be uncomputed;
therefore we can use this multiply-then-add trick. Figure 5 shows how this saves almost half the
gate cost and depth of the squaring, as well as saving an auxiliary register.
|x1⟩
|ctrl⟩
|t0 = 0⟩
|λ⟩
|t1 = 0⟩
|t2 = 0⟩
n
n
n
n
n
squA squ−1
A
-
-
squA squ−1
A
(a) Original circuit [ 27] with squ circuit ex-
panded, squA produces dirty auxiliary qubits
in |t1⟩.
|x1⟩
|ctrl ⟩
|t0 = 0 ⟩
|λ⟩
|t1 = 0 ⟩
n
n
n
n
squ A
-
-
squ −1
A
(b) More eﬃcient version.
Fig. 5: Improvement to the squaring circuit from [27] in the context of elliptic curve point addition.
7
