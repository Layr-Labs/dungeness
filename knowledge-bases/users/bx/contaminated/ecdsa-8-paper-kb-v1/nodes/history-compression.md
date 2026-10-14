---
kind: node
id: history-compression
source: paper section 3.1 and Figure 1
depends_on: [euclid-history]
---

# History compression

One Euclid step has three possible symbols:

```text
(0,0), (1,0), (1,1)
```

Three steps produce 27 valid six-bit patterns. An ad hoc reversible circuit maps them to five bits and clears one wire.

```text
3 raw symbols: 6 bits
compressed block: 5 bits
compressor cost: 5 Toffolis
```

At 402 iterations:

```text
134 blocks * 5 = 670 tape bits
```

The codec is a partial-domain reversible permutation, not standard integer compression.

Consumer: [`bezout-replay.md`](bezout-replay.md).
