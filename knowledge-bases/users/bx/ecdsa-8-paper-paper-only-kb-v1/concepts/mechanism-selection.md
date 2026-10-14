# Mechanism selection

Choose a source by the required interface.

| Need | Primary source | Secondary source |
|---|---|---|
| in-place prime-field multiply or divide | Schrottenloher | Luo et al. |
| fresh-output low-gate multiplication | Litinski | Häner et al. |
| classical-offset addition with little clean workspace | Gidney | Häner et al. |
| one-bit predicate cleanup | Luongo | Gidney |
| whole-register recycling | Luo et al. | Kornerup et al. |
| general time–space scheduling | Kornerup et al. | Häner et al. |
| implicit Euclid transformation | Khattar et al. | Schrottenloher |
| mature integrated affine stack | Häner et al. | Schrottenloher |

## Checklist

```text
field model
operand types
input and output representation
in-place or fresh output
controls
garbage
measurement transcript
inverse
resource convention
```
