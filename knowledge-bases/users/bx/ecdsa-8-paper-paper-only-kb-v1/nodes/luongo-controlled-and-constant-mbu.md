---
kind: node
id: luongo-controlled-and-constant-mbu
source: arXiv:2407.20167, sections 4.2-4.4
depends_on: [luongo-modular-adder-shell]
---

# Controlled and constant MBU variants

**[PAPER]** The same framework covers:

- controlled modular addition;
- modular addition by a constant;
- controlled constant modular addition;
- two-sided comparison.

Representative controlled CDKPM cost:

```text
about 9n+1 -> 8n+0.5 expected Toffoli
```

These variants are relevant because secp256k1 correction constants are classical and replay corrections are often controlled.
