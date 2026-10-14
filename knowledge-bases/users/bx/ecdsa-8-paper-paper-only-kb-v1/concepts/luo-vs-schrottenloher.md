# Luo et al. and Schrottenloher

| Dimension | Schrottenloher | Luo et al. |
|---|---|---|
| Euclid representation | compact branch transcript | explicit shared EEA state |
| Schedule | fixed binary steps plus replay | fixed global four-phase steps |
| Space mechanism | shrinking values share storage with growing history | shrinking remainders share storage with growing coefficients |
| Measurement scale | selected cleanup predicates | complete field-register demolition |
| 256-bit point-add width | about 1,192 qubits | 835 qubits |
| 256-bit point-add gate count | about `2^21.19` | 70.10 million Toffolis |
| Approximation | statistical margins | exact fixed bounds |

## Synthesis

Schrottenloher stores less arithmetic state by delaying coefficient evolution.
Luo stores explicit arithmetic state but proves a tighter physical layout.

Potential combinations must preserve:

- the transcript replay interface;
- exact reconstruction of any measured field value;
- distinct cleanup protocols;
- each source's cost model.
