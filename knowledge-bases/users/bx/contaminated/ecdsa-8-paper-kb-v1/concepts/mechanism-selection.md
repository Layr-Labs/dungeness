# Mechanism selection

Choose by the bottleneck, not by paper headline.

| Observed bottleneck | First source | Secondary source |
|---|---|---|
| replay add/double/fold Toffoli | Schrottenloher | Gidney, Litinski |
| constant controlled correction workspace | Gidney | Luongo |
| one-bit predicate uncomputation | Luongo | Gidney |
| tape/replay simultaneous width | Spooky, Schrottenloher | Khattar |
| obsolete complete field register | Luo | Luongo |
| quotient/history representation | Khattar | Schrottenloher, Luo |
| integrated lifetime/copy overhead | Häner | Spooky |
| full low-space fallback | Luo | Khattar |

## Selection checklist

```text
operand types: quantum/quantum or classical/quantum?
output: in place or fresh register?
modulus: generic, Montgomery, or pseudo-Mersenne?
control: quantum or runtime classical?
garbage: bit, carry vector, field register, or history tape?
recovery: exact oracle available?
peak: does the target phase own max ID?
metric: fixed or expected executed cost?
```

If any answer mismatches the source construction, include the adaptation cost before comparing.
