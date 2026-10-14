---
kind: node
id: resource-estimates
source: paper Tables 1-2
---

# Resource estimates

Point-add circuit, excluding window:

| Variant | Qubits | Toffolis |
|---|---:|---:|
| secp256k1 space | 1192 | `2^21.19` |
| secp256k1 gate | 1446 | `2^20.83` |
| generic space | 1192 | `2^21.78` |
| generic gate | 1446 | `2^21.42` |

Window overhead:

```text
16 qubits
3*2^16 Toffolis per point-add call
```

Full secp256k1 Shor estimate:

```text
28 * (point_add_Toffolis + 3*2^16)
```

Reported totals:

| Variant | Qubits | Full Toffolis |
|---|---:|---:|
| secp256k1 space | 1208 | `2^26.11` |
| secp256k1 gate | 1462 | `2^25.78` |

Connected:

- [`cost-hotspots.md`](cost-hotspots.md)
- [`in-place-modular-multiplication.md`](in-place-modular-multiplication.md)
