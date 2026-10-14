---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 7
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 7

The text below is a page-delimited extraction of the unchanged source PDF.

Shor’s Algorithm.LetPbe a base point andQbe the point of which we com-
pute the discrete logarithm, i.e.,Q= [k]Pfor some unknownk. We use a
version of Shor’s algorithm that can be adapted with the semiclassical Fourier
transform [12]:
1. Create a uniform superposition over two registers of sizen: P
0≤u,v<2n |u⟩|v⟩
2. Apply apoint multiplication unitary: P
0≤u,v<2n |u⟩|v⟩|[u]P+ [v]Q⟩
3. Apply a 2 n-dimensional Fourier transform over the two input registers
4. Measure
One can then retrievekfrom a single measurement result with large success
probability (more than 1/2). Thesemiclassical Fourier transforminterleaves
the operations of the Fourier transform and the point multiplication using a
single recycled control qubit. As a consequence, both qubit and gate count can
be approximated by those of the point multiplication:
|u, v⟩|0⟩ 7→ |u, v⟩|[u]P+ [v]Q⟩.(2)
Letwbe awindowsize, which can be selected depending on the cost of point
addition. The value isw= 16 in [2], and since we have similar costs, we will use
the same later on. We rewriteuandvas:
(
u:=u 0 + 2wu1 + 22wu2 +. . .+ 2(ℓ−1)wuℓ−1
v:=v 0 + 2wv1 + 22wv2 +. . .+ 2(ℓ−1)wvℓ−1
(3)
Then the point multiplication is rewritten as:
[u]P+ [v]Q=
ℓ−1X
i=0
[ui]\([2iw]P) +
ℓ−1X
i=0
[vi]\([2iw]Q).(4)
We can therefore reduce the point multiplication circuit to the following
windowed point addition. Let (P 0, . . . , P2w−1) be awindowof points, then the
point addition circuit does:
|i⟩|R⟩ 7→ |i⟩|R+Pi⟩.(5)
Starting fromO, we just have to compute 2ℓ= (2n/w) times a windowed
point addition circuit, where the windows are precomputed multiples ofPand
Q. Ifi= 0 the multiple isO. The semiclassical Fourier transform works similarly
for windowed additions, with less intermediate measurements since we only have
to interleave the operations between each window.
Point Addition.The point addition circuit uses the strategy of [11]. We can use
formulas for addition of elliptic curve points in affine coordinates, neglecting the
case of doublings (which would happen only with negligible probability) and the
point at infinity. The only special case is fori= 0, where the output register
should be unchanged since we are addingO.
7
