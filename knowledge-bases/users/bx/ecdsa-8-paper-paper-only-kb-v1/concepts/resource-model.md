# Unified resource model

The papers report different quantities:

```text
logical Toffoli or Toffoli-like count
T count
T depth
CNOT count
logical width
expected branch cost
abstract pebbling steps
```

Do not convert one into another without an explicit model.

## Complete comparison unit

A resource comparison must include:

- input and output placement;
- persistent representation;
- workspace lifetime;
- cleanup and phase repair;
- controls;
- approximation assumptions;
- complete caller or wrapper when it changes the interface.

## Information location

Space can move into:

```text
transcript bits
length metadata
explicit coefficients
fresh outputs
classical measurement records
recomputation time
```

Lower logical width does not imply lower gate count or lower total memory.
