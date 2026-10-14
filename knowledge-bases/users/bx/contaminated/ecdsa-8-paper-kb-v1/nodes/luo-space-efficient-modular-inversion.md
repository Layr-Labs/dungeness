---
kind: node
id: luo-space-efficient-modular-inversion
source: arXiv:2607.13816v2 Algorithm 1 and section 6.1
depends_on: [luo-uniform-step-bound, luo-optimized-eea-step]
related: [luo-hadamard-register-recycling, luo-resource-estimates]
---

# Space-efficient modular inversion

**[PAPER]** Forward interface:

```text
|x>|0^n>|0^S>
  -> |x^-1 mod p>|0^n>|Gamma(x)>
```

Algorithm outline:

```text
initialize Work1 with p and coefficient seed
initialize Work2 with x
initialize lengths and phase controls
if x > p/2:
  replace x by p-x and toggle Iter
repeat optimized EEA step 4 ceil(c n) times
select the terminal t' as the inverse
fix its sign using Iter
clear input-independent terminal workspace
retain Gamma(x) for later inverse EEA
```

The input folding `x -> p-x` is used to make the chosen endpoint convention invertible.

Width:

```text
2n + 6 floor(log2 n) + 19
```

At `n=256`, this is 579 qubits for a controlled inversion and 578 without the external control convention used in the companion layout.

The circuit is exact for every nonzero input under the fixed schedule. It is not a clean standalone map until a later inverse EEA erases `Gamma(x)`.

