---
kind: source-page
source_id: arXiv:2407.20167v1
source_pdf: raw/2407.20167v1.pdf
source_page: 10
---

# Measurement-based uncomputation of quantum circuits for modular arithmetic - source page 10

The text below is a page-delimited extraction of the unchanged source PDF.

c0 = 0 M
A
J
c0 ⊕ x0 U
M
A
c0
y0 y0 ⊕ x0 s0
x0
M
A
J
c1 ⊕ x1 U
M
A
x0
y1 y1 ⊕ x1 s1
x1 c2 ⊕ x2 x1
...
...
xn−3
M
A
J
cn−2 ⊕ xn−2
U
M
A
xn−3
yn−2 yn−2 ⊕ xn−2 sn−2
xn−2
M
A
J
cn−1 ⊕ xn−1
U
M
A
xn−2
yn−1 yn−1 ⊕ xn−1 sn−1
xn−1 cn xn−1
yn = 0 0 sn
Figure 8: CDKPM ripple-carry adder of [Cuc+04]. The corresponding significant bits of a = a0a1 ··· an−1 and
b = b0b1 ··· bn−1 are intertwined with each other. The register b is extended by a single qubit to account for the last
carry bit in the addition
ci
M
A
J
ci ⊕ xi
U
M
A
xi ⊕ ci ⊕ ci+1 ⊕ [xi ⊕ ((((((maj(xi, yi, ci)] =ci
yi yi ⊕ xi (ci ⊕ xi) ⊕ (yi ⊕ xi ) ⊕ ci+1 ⊕ [xi ⊕ ((((((maj(xi, yi, ci)] =si
xi ci+1 ci+1 ⊕ [xi ⊕ ((((((maj(xi, yi, ci)] =xi
Figure 9: The combination of MAJ (majority) and UMA (unmajority) gates. Observe that [( ci ⊕ xi)(yi ⊕ xi)] =
xi ⊕ maj(xi, yi, ci) where the majority function maj is given in equation (5) of section 1.3.
x x
y y
xy
=
x T† x
y T† y
|T⟩ T H S xy
Figure 10: The temporary logical- AND construction of Gidney [Gid18]. Here, the decomposition is using T gates,
however, we consider just consider each temporary logical- AND gate implemented using a Tof gate in our paper.
x x
y y
xy
=
x x
y Z y
xy H
Figure 11: Uncomputation of the temp logical- AND by Gidney [Gid18]. Here the circuit uses no T gates. It instead
includes an H gate, a computation basis measurement and a classically controlled C-Z gate.
G-MAJ G-UMA
···
···
···
c i c i
x i x i  c i x i  c i
x i
y i y i  c i y i  c i ( x + y ) i
c i +1 c i +1
Figure 12: Adder block in Gidney’s adder [Gid18]
for each of the n MAJ blocks. In the UMA blocks, the uncomputation of the Tof gate is performed
by a measurement and classically controlled C-Z gate (using MBU). We show a block of Gidney’s
original contruction below.
10
