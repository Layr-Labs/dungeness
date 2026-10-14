---
kind: node
id: generic-controlled-modular-addition
source: paper section 4, Algorithms 8-9
depends_on: [approximate-comparison]
---

# Generic controlled modular addition

Goal:

```text
|c,x,y> -> |c,x,y+c*x mod p>
```

Paper's approximate structure:

```text
controlled ordinary add
high-bit test for result >= p
controlled subtract p
erase reduction bit with controlled high-bit test result < x
```

Dominant operations:

- controlled variable addition;
- controlled full-width constant subtraction.

Specialized alternative: [`pseudo-mersenne-controlled-addition.md`](pseudo-mersenne-controlled-addition.md).
