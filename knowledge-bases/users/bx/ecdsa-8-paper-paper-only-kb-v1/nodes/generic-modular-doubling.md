---
kind: node
id: generic-modular-doubling
source: paper section 4, Algorithms 5-6
depends_on: [approximate-comparison]
---

# Generic modular doubling

Exact starting point:

```text
shift x through one ancilla
subtract p
conditionally add p back
erase reduction flag
```

Paper's generic approximate variant:

```text
shift
compare only high bits against p
conditionally subtract p
erase flag from an output bit relation
```

Dominant remaining cost: one controlled constant operation of width about `n`.

Specialized alternative: [`pseudo-mersenne-doubling.md`](pseudo-mersenne-doubling.md).
