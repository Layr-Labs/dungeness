# Agent pack — Luo et al. low-space ECDLP paper

Use this as a compact implementation brief for arXiv:2607.13816v2. It is source knowledge, not proof that a benchmark candidate works.

## 0. Mission

Improve:

```text
score = average executed Toffoli * peak qubits
```

while preserving:

- point-addition outputs;
- zero garbage in released ancillas;
- relative phase;
- explicit forward/reverse identity;
- untouched benchmark and evaluator.

Labels:

```text
[PAPER]     arXiv:2607.13816v2
[CODE]      companion Qiskit repository at pinned revision
[BENCHMARK] trusted local contract
[INFERENCE] experiment to test
```

## 1. Paper in one screen

The paper gives an exact low-space four-phase EEA. Decreasing remainders and increasing Bézout coefficients share:

```text
Work1: n+3 qubits, t | q | r
Work2: n+3 qubits, shifted/wrapped t' and r'
```

Four logarithmic length registers:

```text
ell_t, ell_q, ell_r', ell_s
```

select location-controlled arithmetic.

Fixed schedule:

```text
c = 3/log2(2+sqrt(3)) ≈ 1.5789734406
T_max = 4 ceil(c n)
T_max(256) = 1620
```

Widths:

```text
inversion  = 2n + 6 floor(log2 n) + 19 = 579 at n=256
point add  = 3n + 6 floor(log2 n) + 19 = 835 at n=256
```

Costs:

```text
inversion < 216.636n^2 Toffoli
point add < 1003n^2 Toffoli
n=256 point add = 70.10M Toffoli
full ECDLP ≈ 2^30.88 Toffoli
```

The `2^30.63` sentence in Section 6.4 is a typo; the formula evaluates to `2^30.88`.

## 2. Most transferable idea: recycle a whole field register

Given obsolete but recomputable `y`:

```text
H^n on y
measure b
reset y to zero
reuse y as workspace
recompute y from surviving data
apply Z^b to recomputed y
uncompute y
```

Measurement creates phase:

```text
(-1)^(b dot y)
```

The `Z^b` correction cancels it.

This lets in-place division use three field registers:

```text
|x>|y>|0> -> |x>|y/x>|0>
```

It is not safely inverted by reversing a gate list. Build and test an explicit inverse protocol with measurement outcomes.

## 3. Second transferable idea: liveness before dynamic arithmetic

The paper proves step-indexed active intervals:

```text
[k_j(T),K_j(T)]
```

for moving arithmetic endpoints.

Try these uses in order:

```text
1. allocator lifetime overlap
2. dirty borrowing from inactive field slices
3. narrower fixed-position operation spans
4. unary selected operation
5. full location-controlled arithmetic
```

Literal location-controlled arithmetic is expensive:

```text
r add/sub: 11(K-k) Toffoli
t add/sub:  9(K-k) Toffoli
swap:       2(K-k) Toffoli
length:    24(K-k) Toffoli
```

## 4. Architecture position

This paper reaches 835 qubits by paying substantial location-selection and arithmetic cost. Its strongest first-use case in a product-scored benchmark is selective:

```text
keep the current verified arithmetic core
add Luo-style register demolition and liveness reuse
```

Do not start with a full four-phase EEA rewrite unless peak width is already proven to dominate the score.

## 5. Benchmark mapping

Paper wrapper:

```text
window index -> precomputed point coordinates
```

Benchmark wrapper:

```text
quantum target point + runtime classical offset point
```

Reuse the existing top-level classical-offset affine schedule. Transfer only the arithmetic/lifetime mechanisms.

Rough direct-port warning:

```text
70.10M * 835 ≈ 58.5B
```

## 6. Recommended experiment sequence

### A. Map peak ownership

Find:

```text
which field values are live at peak
which one becomes obsolete first
whether it is exactly recomputable
```

### B. Tiny phase-sensitive demolition test

At small width:

- exhaust basis states;
- test superpositions;
- run explicit forward/reverse;
- remove one `Z` correction and confirm the test fails.

### C. One real field call site

Recycle one operand around existing inversion cleanup. Record qubit and Toffoli deltas separately.

### D. Liveness-only overlap

Keep arithmetic unchanged and overlap storage proven inactive.

### E. Dirty borrowing

Replace clean helper qubits with restored inactive field bits.

### F. Selector comparison

Microbenchmark unary iteration against the current equality/MCX pattern.

## 7. Acceptance checklist

```text
same base and harness
all trusted shots pass
zero garbage
zero phase error
explicit forward/reverse identity
score product improves
failed hypothesis recorded
```

Companion code revision:

```text
e64aa3c1198d96aeb389e64bc7ae48edbb9712ec
```

Key source files:

```text
under1000_eea_shared_s835_fastdual_wrapped.py
eea_circuit_s835_fastdual.py
eea_circuit_s835_lowaux.py
quadratic_fig15_inplace_s835_fastdual_wrapped.py
point_addition_fig14_s835_fastdual_wrapped_quadratic.py
count_s835_fastdual_wrapped_point_addition_blocks_compiled.py
```
