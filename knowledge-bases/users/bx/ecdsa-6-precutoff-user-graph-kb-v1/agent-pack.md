---
title: Quantum Arithmetic and Measurement-Based Uncomputation Knowledge Base
scope: Six primary-source papers on multiplication, modular addition, constant-workspace addition, spooky pebbling, reversible EEA, and elliptic-curve arithmetic
source_policy: Exact paper versions requested; primary sources only
audience: Quantum-circuit designers and technical reviewers
---

# Quantum Arithmetic and Measurement-Based Uncomputation Knowledge Base

## Purpose and conventions

This knowledge base answers the eighteen supplied questions and records the interface assumptions that matter when reusing the constructions in another arithmetic stack.

- `n` is the relevant register width unless a paper defines it differently.
- "Toffoli cost" means the accounting convention used by the cited paper. Expected costs include the paper's measurement-branch probability.
- A reported construction is not automatically compatible with an in-place canonical prime-field API. Representation, map shape, garbage, controls, and correction state must all match.
- Page numbers refer to the PDF page labels.

## Quick reference

| Paper | Main reusable idea | Headline exact result | Main import warning |
|---|---|---|---|
| Litinski | Replace controlled adds by controlled add-subtracts | Non-modular multiplier: \(n^2+4n+3\) Toffolis | Prime-modulus circuit is out-of-place and assumes Montgomery representation |
| Luongo et al. | Measure a one-bit predicate and repair only one branch | Gidney modular add: \(3.5n\); controlled: \(4.5n+0.5\), in expectation | Repair oracle must satisfy the one-bit self-adjoint XOR-oracle contract |
| Gidney | Vent carries into deferred phase corrections | \(4n\pm O(1)\) with 3 clean ancillas, or \(3n\pm O(1)\) with 2 clean and \(n-2\) dirty ancillas | Measurements leave classical phase-correction obligations |
| Kornerup et al. | Recycle qubits by replacing values with phase ghosts | \(n\leq\binom{m+s-2}{s-2}+1\) gives an \(s\)-pebble, \(O(mn)\)-step line pebbling | Classical measurement records remain live |
| Khattar et al. | Store an EEA execution trace instead of materializing Bézout polynomials | Direct division applies the EEA transition product to \([0,A]^T\) | Quantitative counts are specialized to polynomial arithmetic over \(\mathrm{GF}(2^b)\) |
| Häner et al. | Normalize four binary-EEA cases with swaps and fuse correction into cleanup | Fixed \(2n\) rounds; \(2n-k\) cleanup doublings correct the pseudo-inverse | Arithmetic is Montgomery-form and tightly scheduled around producer/consumer reuse |

## 1. Litinski, *Quantum schoolbook multiplication with fewer Toffoli gates*

Source version: arXiv:2410.00899v1.[^1]

Retrieval tags: `schoolbook multiplication`, `controlled add-subtract`, `Montgomery multiplication`, `Toffoli count`, `out-of-place`

### KB-LIT-01 - Replacement for shifted controlled addition

**Answer.** Each shifted controlled addition is replaced by a **controlled add-subtract**. With control bit \(x_k\), it adds \(2^k y\) when \(x_k=1\), but subtracts \(2^k y\) when \(x_k=0\), represented in the enlarged positive-integer register as adding \(2^{n+k}-2^k y\). A controlled add-subtract has the Toffoli cost of an uncontrolled adder: \(n\) with carry-out or \(n-1\) without carry-out. (pp. 1-2, Figs. 1-2.)[^1]

For the \(k\)-th multiplication step, the amount added is

\[
(1-x_k)2^{n+k}+(2x_k-1)2^k y.
\]

### KB-LIT-02 - Exact intermediate expression and non-modular cost

After all \(n\) controlled add-subtract operations, the paper gives the intermediate value

\[
\sum_{k=0}^{n-1}\left((1-x_k)2^{n+k}+(2x_k-1)2^k y\right)
=2xy+2^{2n}-2^n(x+1+y)+y.
\]

The global corrections are:

1. add \(2^n(x+1)\);
2. subtract \(2^{2n}+y\);
3. add \(2^n y\);
4. divide by two by relabeling the qubits.

The reported total for the non-modular, \(2n\)-bit-output schoolbook multiplier is

\[
\boxed{n^2+4n+3\ \text{Toffoli gates}}.
\]

This is compared with \(2n^2+n\) for the controlled-adder construction. (pp. 1-2, Table 1 and Fig. 2.)[^1]

### KB-LIT-03 - Prime-field interface limitation

**Important limitation.** The paper's prime-modulus construction is an **out-of-place Montgomery-representation multiplier**. Its inputs are assumed to be stored in Montgomery form; each `ModMultStep` also contributes garbage, and full cleanup may require copying the result to another register and reversing the multiplier. (pp. 2-4, Fig. 3.)[^1]

Therefore it is not a drop-in implementation of an API such as

\[
|a\rangle_{\mathrm{canonical}}\longmapsto |a b\bmod p\rangle_{\mathrm{canonical}}
\]

performed in place. Importing it requires, at minimum, a representation plan for entering and leaving Montgomery form and a decision about the separate result and garbage registers. If the surrounding circuit requires a canonical residue after every operation, conversion and cleanup costs must be included.

## 2. Luongo et al., *Measurement-based uncomputation of quantum circuits for modular arithmetic*

Source version: arXiv:2407.20167v1.[^2]

Retrieval tags: `MBU lemma`, `modular addition`, `Gidney adder`, `controlled modular addition`, `expected Toffoli`

### KB-LUO-01 - The two branches of the one-bit MBU lemma

The lemma starts with

\[
\sum_x\alpha_x|x\rangle_A|g(x)\rangle_G
\]

and requires a self-adjoint oracle

\[
U_g|x\rangle_A|b\rangle_G
=|x\rangle_A|b\oplus g(x)\rangle_G.
\]

Apply \(H\) to \(G\) and measure \(G\) in the computational basis:

- **Outcome 0, probability \(1/2\):** the register is already uncomputed, leaving
  \[
  \sum_x\alpha_x|x\rangle_A|0\rangle_G.
  \]

- **Outcome 1, probability \(1/2\):** the data register carries the phase
  \[
  \sum_x\alpha_x(-1)^{g(x)}|x\rangle_A|1\rangle_G.
  \]
  The repair applies \(H\) to \(G\), then \(U_g\), then another \(H\) and a NOT on \(G\). Phase kickback cancels \((-1)^{g(x)}\) and resets \(G\) to \(|0\rangle\).

**Repair condition.** The plug-and-play statement depends on \(U_g\) being the self-adjoint XOR oracle above. The expected nonlinear cost is half the cost of invoking that repair oracle, because only the outcome-1 branch uses it. (Lemma 4.1, p. 35.)[^2]

### KB-LUO-02 - Gidney modular-adder costs after MBU

The reported expected costs are:

| Construction | Expected Toffoli cost | Ancillas |
|---|---:|---:|
| Gidney modular adder | \(\boxed{3.5n}\) | \(2n+3\) |
| Gidney controlled modular adder | \(\boxed{4.5n+0.5}\) | \(2n+3\) |

For the uncontrolled circuit the decomposition is

\[
n+n+n+\frac{n}{2}=3.5n.
\]

For the controlled circuit it is

\[
2n+n+n+\frac{n+1}{2}=4.5n+0.5.
\]

The halved term is the final comparator used to erase the reduction flag. (Theorems 4.4 and 4.9, pp. 36 and 38-39.)[^2]

### KB-LUO-03 - Where the external control is actually required

Only two of the four high-level subroutines need the **external** control \(c\):

1. the first addition, producing \(c x+y\);
2. the final comparison used to uncompute the reduction flag.

The middle comparison against \(p\) is unconditional. The subtraction of \(p\) is controlled by the internally computed comparison/reduction flag, not directly by \(c\). This is why controlling every gate or every modular-adder subroutine would over-control the circuit. (Proposition 3.9, p. 28.)[^2]

## 3. Gidney, *A Classical-Quantum Adder with Constant Workspace and Linear Gates*

Source version: arXiv:2507.23079v1.[^3]

Retrieval tags: `constant workspace`, `classical-quantum adder`, `venting`, `carry identity`, `free outer control`

### KB-GID-01 - Principal workspace/Toffoli tradeoffs

The paper's two headline operating points are:

| Clean ancillas | Dirty ancillas | Toffoli cost |
|---:|---:|---:|
| 3 | 0 | \(\boxed{4n\pm O(1)}\) |
| 2 | \(n-2\) | \(\boxed{3n\pm O(1)}\) |

The second construction uses a dirty secondary register for carry-xor operations. The first obtains constant total workspace by splitting the target into two halves and letting each half borrow the other as dirty workspace at different stages. (pp. 1, 3, and 7; Figs. 4-5.)[^3]

### KB-GID-02 - Carry identity used for venting

Define

\[
x'=x+d+c_0
\]

and

\[
\operatorname{carry}(x,d,c_0)
=x\oplus d\oplus(x+d+c_0).
\]

The identity is

\[
\boxed{\operatorname{carry}(\sim x',d,c_0)
=\operatorname{carry}(x,d,c_0)}.
\]

Thus the carries can be recomputed from values available after the addition. They are "Z-redundant": measuring a carry qubit in the \(X\) basis frees the qubit, while a minus outcome leaves a known deferred phase-flip task. The paper calls this conversion from carry garbage into phase obligations **venting**. (Eq. 8 and Sec. 2.2, p. 3.)[^3]

### KB-GID-03 - Why an outer control adds no Toffolis

The classical offset enters the circuit through its bits \(d_k\). To control the whole addition:

- replace every hardwired \(d_k=0\) by 0;
- replace every hardwired \(d_k=1\) by the outer control qubit.

The \(d_k\) values are used only to invert controls or to control bit flips. Substituting the outer control into those positions does not promote any existing operation into a higher-controlled nonlinear gate, so the paper counts **no additional workspace and no additional Toffolis**. (Sec. 2.4, p. 7; Fig. 6.)[^3]

## 4. Kornerup, Sadun, and Soloveichik, *Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements*

Source version: arXiv:2110.08973v3.[^4]

Retrieval tags: `spooky pebble game`, `ghosting`, `measurement record`, `time-space tradeoff`, `binomial bound`

### KB-KSS-01 - Ghosting transformation and precondition

A circuit \(C\) ghosts a register if it implements

\[
\boxed{
\sum_i\alpha_i|x_i\rangle|y_i\rangle
\xrightarrow{C}
\sum_i\alpha_i(-1)^{b\cdot y_i}|x_i\rangle|0\rangle
}
\]

while returning \(b\) as a classical bitstring. The logical value \(y_i\) has been erased from the qubits and replaced by a phase depending on the retained measurement record. (p. 4.)[^4]

**Precondition.** The labels \(x_i\) must be pairwise distinct. Without that condition, different basis components can collapse onto the same \(|x\rangle|0\rangle\) state and interfere, so the proposed map need not preserve the norm. The distinct-label condition prevents that collision. (pp. 4-5.)[^4]

### KB-KSS-02 - Binomial line-length relation

The exact relation appears in two closely related forms:

- **Unghosting, Lemma 3.5:** if
  \[
  \boxed{n\leq\binom{m+s-1}{s-1}},
  \]
  a line of length \(n\) can be unghosted with at most \(s\) pebbles and \(O(mn)\) steps.

- **Pebbling, Theorem 3.6:** after the one-pebble conversion,
  \[
  \boxed{n\leq\binom{m+s-2}{s-2}+1},
  \]
  a line of length \(n\) can be pebbled with at most \(s\) pebbles and \(O(mn)\) steps.

The paper's summary table suppresses the harmless \(+1\) and presents the condition in the form \(\binom{m+s-2}{s-2}\geq n\). (pp. 3 and 10.)[^4]

### KB-KSS-03 - Memory that remains live

The recycled qubits do not eliminate the full memory obligation. The measurement bitstring \(b\) must remain in **classical ancillary memory** from ghosting until the original value can be recomputed and the phase can be removed. Correspondingly, the paper reduces quantum memory but not total memory measured as classical bits plus qubits. (pp. 2, 5-6.)[^4]

Operationally, a ghosted register has two pieces of outstanding state:

1. a reusable standard-basis qubit register;
2. a classical record describing the phase correction that must eventually be discharged.

## 5. Khattar et al., *Verifiable Quantum Advantage via Optimized DQI Circuits*

Source version: arXiv:2510.10967v1.[^5]

Retrieval tags: `reversible EEA`, `Bezout coefficients`, `Dialog representation`, `direct modular division`, `GF(2^b)`

### KB-KHA-01 - Explicit versus implicit Bézout access

Write each EEA step as a small transition matrix \(\tau_i\), with

\[
\tau_{\mathrm{total}}=\tau_m\tau_{m-1}\cdots\tau_1.
\]

- **Explicit access:** compute and store the full product \(\tau_{\mathrm{total}}\), including the coefficient arrays of the final Bézout polynomials. This is required when later logic needs the polynomial coefficients as ordinary data.

- **Implicit access:** store a compact representation of each \(\tau_i\), without multiplying the sequence into full Bézout polynomials. A consumer is rewritten to replay the transformations on an appropriate vector. The Bézout object exists as an executable transformation sequence, not as a materialized coefficient register.

Both approaches target leading-order space \(2nb+O(\log_2 n)\), but the implicit construction uses the cheaper constant-time, division-free EEA structure. (Secs. II.B.1-3, pp. 8-13.)[^5]

### KB-KHA-02 - Direct division without materializing \(B^{-1}\)

Assume \(P\) is irreducible and \(\gcd(P,B)=1\). First execute the EEA on \((P,B)\) to obtain the ordered transition sequence \(\tau_1,\ldots,\tau_m\). Instead of extracting the Bézout polynomial \(B^{-1}\), apply

\[
\tau_{\mathrm{total}}
\]

to the different input vector

\[
\begin{bmatrix}0\\A\end{bmatrix}.
\]

Linearity gives

\[
\boxed{
\tau_{\mathrm{total}}
\begin{bmatrix}0\\A\end{bmatrix}
=
\begin{bmatrix}AB^{-1}\\0\end{bmatrix}
\pmod P
}.
\]

The quotient is produced directly by replaying the EEA transformations; no register ever holds the full inverse \(B^{-1}\). The paper reports a leading gate cost of \(4n^2\) underlying field multiplications for this implicit direct-division route, versus \(7n^2\) for its explicit invert-then-multiply route. (p. 9, Table IV.)[^5]

### KB-KHA-03 - What the Dialog encodes and transfer limitation

The **Dialog** is the EEA execution trace represented as the ordered sequence of small invertible transition matrices. For the constant-time division-free construction, it is concretely the list of update coefficients \(c_i\) and conditional swap decisions. The name is also a mnemonic for the elementary operations:

- **D**oubling or shifting;
- **I**nversion or swapping;
- **A**ddition/subtraction;
- with the representation behaving somewhat like a **log** because multiplication and division are easy to express while addition is not.

For degree-\((n-1)\) polynomial inputs, the paper's Dialog has \(2n\) field elements. (pp. 10-13.)[^5]

**Why the numerical results do not directly transfer to large-prime integer arithmetic.** The resource analysis is for polynomial EEA and Reed-Solomon decoding over binary extension fields \(\mathrm{GF}(2^b)\). In characteristic two:

- addition is bitwise XOR;
- quantum-classical multiplication and squaring can be CNOT-only linear maps;
- the quoted multiplication, inversion, and MBU costs use specially optimized \(\mathrm{GF}(2^b)\) circuits.

Integer arithmetic modulo a large prime has carry propagation, integer comparison and reduction, different shift/division semantics, and different primitive costs. The **implicit-transition representation idea** is portable, but the paper's Toffoli and qubit totals are not portable without rebuilding the transition matrices, fixed-round schedule, and cost model for the integer domain. (Sec. II.C and Appendix C, pp. 13 and 39-41.)[^5]

## 6. Häner et al., *Improved quantum circuits for elliptic curve discrete logarithms*

Source version: IACR ePrint 2020/077.[^6]

Retrieval tags: `Kaliski inversion`, `binary EEA`, `pseudo-inverse`, `Montgomery inverse`, `pebbling`, `workspace reuse`

### KB-HAN-01 - Normalizing the four Kaliski cases

The original round has four branches depending on parity and ordering. The improved formulation uses a swap bit \(b_{\mathrm{swap}}\) to orient all cases into one shared body:

1. set \(b_{\mathrm{swap}}=0\);
2. if \(u\) is even and \(v\) is odd, **or** both are odd and \(u>v\), swap \(u\leftrightarrow v\) and \(r\leftrightarrow s\), then set \(b_{\mathrm{swap}}=1\);
3. if both oriented values are odd, perform
   \[
   v\leftarrow v-u,\qquad s\leftarrow r+s;
   \]
4. unconditionally perform
   \[
   v\leftarrow v/2,\qquad r\leftarrow 2r;
   \]
5. if \(b_{\mathrm{swap}}=1\), swap both pairs back.

Thus controlled swaps choose the register roles, while subtraction/addition, halving, and doubling appear only once in the round body. The lower auxiliary bit and the round-state bit \(m_i\) determine the swap. (Sec. 4.2, pp. 8-9; Figs. 6-7.)[^6]

### KB-HAN-02 - Fixed rounds and integrated pseudo-inverse correction

For \(n\)-bit inputs, the classical Kaliski execution uses some \(k\) with

\[
n\leq k\leq 2n.
\]

The reversible circuit always executes \(\boxed{2n}\) scheduled rounds; only \(k\) rounds modify the EEA state. A counter records \(2n-k\), and the initial output is the pseudo-inverse

\[
x^{-1}2^{-n+k}\pmod p.
\]

The desired Montgomery inverse is

\[
x^{-1}2^n\pmod p,
\]

so the copied output needs exactly \(2n-k\) modular doublings.

The paper folds these doublings into inverse-circuit cleanup. During reversal of the \(2n\) rounds, the same round control selects either:

- uncomputing an active division round; or
- doubling the copied output for an inactive round.

These operations can run in parallel, so the variable correction is completed during cleanup without a separate correction pass or an increase in total gate count. (Sec. 4.2, p. 8.)[^6]

### KB-HAN-03 - Producer/consumer and workspace-reuse examples

**Producer/consumer fusion.** To compute \(xy+z\), the paper keeps the multiplication's auxiliary state alive, replaces Bennett's result-copy CNOT layer by the addition into \(z\), and only then reverses the multiplier. The cost becomes one multiplication plus one addition, rather than two multiplications plus one addition. Applied to squaring followed by subtraction in point addition, this saves almost half the squaring cost and depth and removes an auxiliary register. (Sec. 4.1, p. 7; Fig. 5.)[^6]

**Workspace reuse.** After modular inversion, three registers contain known values \(0\), \(1\), and \(p\). The circuit clears them with at most \(3n\) parallel X gates and reuses their qubits as the workspace for modular multiplication before completing inversion uncomputation. (Sec. 4.2, pp. 8-10; Fig. 8.)[^6]

## Cross-paper integration rules

### 1. Normalize the representation before comparing costs

These papers operate across several incompatible value representations:

- ordinary binary integers;
- residues modulo \(2^n\);
- Montgomery residues modulo an odd prime;
- polynomials modulo an irreducible polynomial;
- field elements of \(\mathrm{GF}(2^b)\);
- implicit EEA transition traces.

A Toffoli improvement inside one representation can be erased by conversion costs if the surrounding algorithm expects another representation.

### 2. Record the map shape

For every imported component, specify whether its contract is:

- in-place or out-of-place;
- clean-output or garbage-producing;
- exact or expected-cost;
- unitary-only or measurement-assisted;
- canonical-output or scaled/pseudo-inverse output.

Litinski's prime multiplier and Häner et al.'s Montgomery arithmetic are especially sensitive to these distinctions.

### 3. Treat measurement outcomes as live data dependencies

MBU, venting, and ghosting free qubits but create a classical record and a phase-correction obligation. A valid scheduler must track:

- where the classical outcome is stored;
- which later computation can reproduce the measured Boolean function;
- the last point before a non-computational-basis use of the recycled register;
- whether repair is deterministic, branch-dependent, or only accounted for in expectation.

### 4. Distinguish an external control from internal predicate controls

A modular arithmetic block may contain internal controlled subtraction even when most of the block does not need the caller's control. Luongo et al. show that only the first adder and final cleanup comparator need the external control. Gidney shows an even stronger constant-offset property: the caller's control can replace hardwired offset bits without new Toffolis.

### 5. Prefer producer/consumer fusion before black-box optimization

Häner et al.'s multiply-then-add and squaring-then-subtract examples show that using a producer's result before reversing its garbage can remove an entire recomputation. This optimization changes the circuit interface and lifetime schedule, and therefore is invisible if arithmetic routines are costed only as isolated black boxes.

### 6. Do not mix cost models without translation

The sources variously report:

- Toffoli count;
- expected Toffoli count;
- T count and T depth;
- calls to an underlying field multiplier;
- qubits split into clean, dirty, quantum, and classical memory.

Comparisons should first translate every candidate into a common primitive library, measurement model, and workspace convention.

## Sources

1. Daniel Litinski. [*Quantum schoolbook multiplication with fewer Toffoli gates*](https://arxiv.org/abs/2410.00899v1). arXiv:2410.00899v1, 2024.
2. Alessandro Luongo, Antonio Michele Miti, Varun Narasimhachar, and Adithya Sireesh. [*Measurement-based uncomputation of quantum circuits for modular arithmetic*](https://arxiv.org/abs/2407.20167v1). arXiv:2407.20167v1, 2024.
3. Craig Gidney. [*A Classical-Quantum Adder with Constant Workspace and Linear Gates*](https://arxiv.org/abs/2507.23079v1). arXiv:2507.23079v1, 2025.
4. Niels Kornerup, Jonathan Sadun, and David Soloveichik. [*Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements*](https://arxiv.org/abs/2110.08973v3). arXiv:2110.08973v3, 2025.
5. Tanuj Khattar et al. [*Verifiable Quantum Advantage via Optimized DQI Circuits*](https://arxiv.org/abs/2510.10967v1). arXiv:2510.10967v1, 2025.
6. Thomas Häner, Samuel Jaques, Michael Naehrig, Martin Roetteler, and Mathias Soeken. [*Improved quantum circuits for elliptic curve discrete logarithms*](https://eprint.iacr.org/2020/077). IACR Cryptology ePrint Archive, Report 2020/077, 2020.

[^1]: Litinski, *Quantum schoolbook multiplication with fewer Toffoli gates*, arXiv:2410.00899v1.
[^2]: Luongo et al., *Measurement-based uncomputation of quantum circuits for modular arithmetic*, arXiv:2407.20167v1.
[^3]: Gidney, *A Classical-Quantum Adder with Constant Workspace and Linear Gates*, arXiv:2507.23079v1.
[^4]: Kornerup, Sadun, and Soloveichik, *Tight Bounds on the Spooky Pebble Game*, arXiv:2110.08973v3.
[^5]: Khattar et al., *Verifiable Quantum Advantage via Optimized DQI Circuits*, arXiv:2510.10967v1.
[^6]: Häner et al., *Improved quantum circuits for elliptic curve discrete logarithms*, IACR ePrint 2020/077.
