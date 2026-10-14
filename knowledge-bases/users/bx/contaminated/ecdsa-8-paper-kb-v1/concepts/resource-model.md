# Unified resource model

## Four different quantities

Keep these separate:

```text
paper logical Toffoli
emitted benchmark Toffoli
average executed benchmark Toffoli
physical fault-tolerant cost
```

The current score uses only average executed benchmark Toffoli and hard maximum qubit ID.

## Space representations in the papers

| Representation | Quantum state retained |
|---|---|
| Schrottenloher | compact branch history plus two replay values |
| Luo | explicit shared EEA values and length metadata |
| Khattar explicit | remainders, coefficients, in-register quotient |
| Khattar Dialog | shrinking polynomial plus growing transition list |
| Spooky/Luongo/Gidney | fewer coherent values plus classical phase outcomes |
| Häner | scheduled arithmetic intermediates and reused workspaces |

All store the information needed for reversibility somewhere. Qubit reduction usually moves it into time, classical outcomes, or a different representation.

## Current peak anatomy

**[BENCHMARK]** The ping-pong replay peak is approximately:

```text
history/sign tape
+ two coefficient/numerator-scale registers
+ residual walk state
+ chunk/fold carry ladder
+ controls
```

Specific counts vary by revision. Re-profile rather than copying a historical total.

## Exchange-rate rules

A qubit-saving mechanism is attractive when:

```text
added executed Toffoli < T·saved_qubits/(Q-saved_qubits)
```

Common false wins:

- fewer conceptual live wires but same maximum ID;
- lower paper width with a fresh benchmark accumulator;
- expected MBU savings charged as emitted fixed gates;
- moving work to a branch that fires frequently;
- replacing a local floor with a higher-level asymptotic construction;
- qubit reduction outside the peak interval.

## Correct comparison unit

Compare complete compatible shells:

```text
input/output placement
workspace lifetime
cleanup and phase repair
controls
modulus representation
failure model
```

Never compare only the inner adder or multiplier count.
