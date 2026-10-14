---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 10
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 10

The text below is a page-delimited extraction of the unchanged source PDF.

order to ensure a large success probability on random inputs, we will therefore
choose an appropriate constantc iter ≃2.4 (four standard deviations) and use a
fixed number of 1.413n+c iter
√niterations.
Second, the number of qubits. At the beginning of the algorithm,uandv
are stored on 2nqubits. Each iteration produces not two, but 1.5 bits of garbage
on average. Indeed, we only need to storeb 0&b1 ifb 0 = 1. So the total number
of output bits that can be expected is 1.5×(1.413 +O( √n)) = 2.12n+O( √n),
and this is the minimal number of qubits with which we can run the algorithm.
This situation is very similar to the Jacobi symbol algorithm in [4]: the amount
of reduction of (u, v) and the number of garbage bits produced per iterate are
the same.
In order to optimize the space, we useregister sharing. There exists apadding
amountc pad
√n, withc pad ≃2.3, such that, with high probability, at each iter-
ationj, the current values ofuandveach fit on:n−0.5 log 2(8/3)i+c pad
√n
bits. This is also experimentally observed. Therefore:
–Operations onuandvare performed on these sub-registers only;
–We use the cleared qubits to store the garbage bits, ensuring a total space
in 2.12n+O( √n).
The choice ofc pad andc iter control the success probability of the algorithm
when called on random inputs. According to our experiments,c pad = 2.3 and
citer = 2.4 ensure a success probability large enough so that the point addition
circuit succeeds on 10 000 random inputs.
Garbage Encoding.Compared to [4], we modify the storage of garbage bits.
Previously we would have used a register in whichb0 andb 0&b1 are queued using
controlled-shifts. The issue is that the shifts are costly, and also, this makes the
total size of the garbage vary, so we would need anotherO( √n) bits of space to
absorb this variation. We use a simpler method here.
Consider three successive iterations producing three pairs of bits. Since these
bits are (b0, b0&b1) for someb 0, b1, they can only be (0,0), (1,0) or (1,1). There
are 33 = 27<2 5 possible values in input, so we cancompressthis input value
into 5 bits, releasing one bit. We define an ad-hoc quantum circuit which does
this in-place with 5 Toffoli gates, shown in Figure 1.
With this, our Euclidean algorithm circuit uses exactly (1.413n+citer
√n)/3×
5≃2.355n+O( √n) garbage bits. While this is asymptotically more, the com-
pression step is much more efficient than the previous encoding (accounting at
the end for a negligible cost), and the garbage register has now a fixed size.
3.2 Using the Garbage Bit-Vector
As we said above, in the EEA, one also maintains registers (r, s) for the B´ ezout
coefficints which are updated depending onb 0 andb 0&b1. If we start the Eu-
clidean algorithm with inputs (u, v) := (q, x), and then run the updates on
the B´ ezout coefficients (r, s) := (1,0), at the end of the algorithm we have
(r, s) = (0, x−1 modq).
10
