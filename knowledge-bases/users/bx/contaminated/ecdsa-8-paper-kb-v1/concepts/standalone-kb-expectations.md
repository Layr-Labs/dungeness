# Standalone-paper KB expectations

If each paper were supplied alone to an implementation agent:

| Paper | Likely usefulness | Main failure mode |
|---|---|---|
| Schrottenloher | high | literal wrapper mismatch and approximation risk |
| Gidney 2025 | high for local primitives | wrong operand model |
| Luongo | medium-high | dynamic phase semantics omitted |
| Litinski | medium | out-of-place multiplier treated as in place |
| Spooky Pebbling | medium | generic checkpointing repeated despite local negative |
| Luo | medium for space ideas | headline 835 qubits overvalued despite 70.10M Toffoli |
| Khattar | exploratory | polynomial-field counts transferred literally |
| Häner | reliable baseline | older design mistaken for frontier |

The unified KB is stronger because it supplies the missing incompatibility checks and current benchmark context.
