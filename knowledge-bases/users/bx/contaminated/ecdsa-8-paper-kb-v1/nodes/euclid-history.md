---
kind: node
id: euclid-history
source: paper section 3.1, Algorithm 2
---

# Euclid history construction

Input:

```text
(u,v)=(p,x), u odd
```

One fixed iteration:

```text
b0 = v mod 2
b1 = u > v
record (b0, b0&b1)
if b0&b1: swap(u,v)
if b0:    v -= u
v >>= 1
```

Expected iterations:

```text
L ~= 1.413n
stddev ~= 0.6*sqrt(n)
```

The released parameters use four-standard-deviation-like slack.

Outputs a history tape and ends at `(1,0)` with high probability.

Connected nodes:

- [`register-sharing.md`](register-sharing.md)
- [`history-compression.md`](history-compression.md)
- [`bezout-replay.md`](bezout-replay.md)
- [`failure-model.md`](failure-model.md)
