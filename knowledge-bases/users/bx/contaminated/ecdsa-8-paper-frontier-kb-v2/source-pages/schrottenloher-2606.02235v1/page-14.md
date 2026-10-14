---
kind: source-page
source_id: arXiv:2606.02235v1
source_pdf: raw/2606.02235v1.pdf
source_page: 14
---

# Optimized Point Addition Circuits for Elliptic Curve Discrete Logarithms - source page 14

The text below is a page-delimited extraction of the unchanged source PDF.

These circuits only need to work when their inputs are drawn uniformly
at random, with a single exception. During the B´ ezout reconstruction (Algo-
rithm 3), for the firstc iter
√niterations, we have to handle the case where
x+y=q. This should not appear if we pick the inputs at random, but it
does appear in our case for the first empty iterations of the algorithm.
Our starting points for these two circuits are taken from [20]. We start by
simplifying the comparisons as shown above, then we simplify them further using
the special form of the primeq. In the following, we give the circuits as pseu-
docode which is similar to our python code. The commands used in pseudocode
are:inputto allocate an input register (which is also output), of a given type,
ancto allocate ancillas, basic gates, operations on registers such asshift_right,
sub(subtraction),cadd(controlled addition),lt(lower than). All these oper-
ations are in-place, andltXORs the result of the comparison to its last input
register.cltis the controlled version. We use “+” to denote concatenation of
registers, seen as lists of qubits.
Doubling.On inputx, the doubling circuit of [20] does a shift, a subtraction by
q, and a controlled addition byq. This is given in Algorithm 5.
Algorithm 5Exact modular doubling circuit from [20].
x_reg = input(ModIntType(q))
anc1, anc2 = anc(1), anc(1)
shift_right(x_reg + anc1, 1)
sub_uint(q, x_reg + anc1 + anc2)
cadd_uint(anc2, q, x_reg + anc1)
x(anc2)
cx(x_reg[0], anc2)
Our “efficient” modular doubling, which works for any prime, is given in Al-
gorithm 6. The only non-exact step is the comparison, where we take the most
significant bits of the current register andq, whereas the exact version of this
circuit would have compared the entire numbers. We notice that the cost of mod-
ular doubling has been reduced to approximately onen-bit controlled constant
addition.
Whenqis a pseudo-Mersenne prime of the form 2 u −f, wheref≪2 u, we
can further simplify this circuit. Indeed, we can further approximate the com-
parison by just checking whether the MSB is 1, and in that case, the controlled-
subtraction byqbecomes an erasure of the MSB, followed by addingfinto the
registerx. Sincefis small, we only need to add it into the LSBs (since carries
will only propagate a certain amount). The exact range determines the success
probability of the algorithm. This is given in Algorithm 7.
Addition.On inputx, y, the controlled modular addition circuit of [20] does a
controlled addition, followed by a subtraction ofq, a controlled addition ofq
14
