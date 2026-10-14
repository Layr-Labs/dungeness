# Litinski: controlled add-subtract multiplication

Source: arXiv:2410.00899v1, *Quantum schoolbook multiplication with fewer
Toffoli gates*.

## Controlled add-subtract

**[EVIDENCE]** The paper replaces a controlled addition, whose inactive branch
is identity, with a choice between addition and subtraction. Clifford bit
complements convert an ordinary ripple adder into this add-subtract primitive.
Without carry-out it costs `n-1` Toffolis; with carry-out it costs `n`. See
[page 1](../source-pages/litinski-2410.00899v1/page-01.md).

The branch behavior is:

```text
control = 1 -> add
control = 0 -> subtract
```

The unwanted subtraction branches are corrected globally after the shifted
accumulation.

## Non-modular multiplication

**[EVIDENCE]** After the shifted add-subtract sequence, the accumulator equals

```text
2xy + 2^(2n) - 2^n(x+1+y) + y.
```

The paper removes the extra terms with a small sequence of additions,
subtractions, and a division by two implemented by relabeling. The resulting
`n`-by-`n` fresh-output multiplier costs `n^2+4n+3` Toffolis in the stated
model. See [page 2](../source-pages/litinski-2410.00899v1/page-02.md).

**[EVIDENCE]** Truncating the construction modulo `2^n` simplifies the
corrections and gives a count of `0.5n^2+1.5n` Toffolis. See
[page 2](../source-pages/litinski-2410.00899v1/page-02.md).

## Prime-modulus Montgomery multiplication

**[EVIDENCE]** The prime-modulus construction uses Montgomery representation
and partitions the multiplier into windows of `w` bits. Each window combines
shifted controlled add-subtracts, lookup-selected reduction data, algebraic
corrections, and a radix division by relabeling. The reported count is

```text
n^2 + 6n + (n/w)(2^w + 3*2^(w/2) + 3n - 3),
```

with an approximate choice

```text
w ~= log2(n/log2(n)) + 2.
```

See [pages 2–4](../source-pages/litinski-2410.00899v1/page-02.md).

## Interface and cleanup

**[EVIDENCE]** The main non-modular interface preserves both inputs and writes
the product into a fresh `2n`-qubit output:

```text
|x>|y>|0> -> |x>|y>|xy>.
```

The windowed modular construction emits garbage associated with the window
steps. The paper describes copying the product and reversing the multiplier to
clean that garbage. See
[pages 1–3](../source-pages/litinski-2410.00899v1/page-01.md).

**[EVIDENCE]** The gate reduction depends on applying the signed transformation
to the complete shifted-add sequence and then performing its global
corrections. It is not a bitwise replacement rule for an isolated controlled
addition. See
[pages 1–2](../source-pages/litinski-2410.00899v1/page-01.md).
