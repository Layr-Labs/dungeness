# Cross-paper arithmetic primitives

| Primitive family | Operand model | Representation | Source |
|---|---|---|---|
| compact Euclid replay | quantum–quantum | canonical prime field | Schrottenloher |
| controlled add-subtract | quantum controls and addends | binary or Montgomery | Litinski |
| one-bit measured cleanup | Boolean function of retained data | representation independent | Luongo |
| vented-carry offset addition | classical offset, quantum target | modulo `2^n` | Gidney |
| exact active-window EEA | quantum field values | canonical prime field | Luo et al. |
| Dialog transition replay | polynomial vectors | extension-field polynomial model | Khattar et al. |
| windowed Montgomery stack | field values in Montgomery form | generic prime field | Häner et al. |

## Selection rule

Do not select by headline gate count alone. Match:

```text
operand types
output placement
number representation
control semantics
garbage and cleanup
available workspace
```

See [`../nodes/paper-interface-boundaries.md`](../nodes/paper-interface-boundaries.md).
