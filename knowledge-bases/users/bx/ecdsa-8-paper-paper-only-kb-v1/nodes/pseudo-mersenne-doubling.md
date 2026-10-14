---
kind: node
id: pseudo-mersenne-doubling
source: paper section 4, Algorithm 7
depends_on: [secp256k1-prime]
---

# Pseudo-Mersenne modular doubling

For `p=2^256-f`:

```text
shift x through overflow bit
if overflow:
    add f to a bounded low-bit slice
erase overflow
```

The retained low slice must include enough margin for the carry chain induced
by adding `f`.

Failure condition: the addition of `f` propagates a carry past the retained slice.

Used heavily by [`bezout-replay.md`](bezout-replay.md).
