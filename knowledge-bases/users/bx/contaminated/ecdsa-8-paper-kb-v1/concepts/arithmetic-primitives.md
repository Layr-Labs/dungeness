# Cross-paper arithmetic primitives

## Addition families

```text
quantum-quantum ripple floor       current replay / older Gidney
controlled add-subtract            Litinski
classical constant, low workspace  Gidney 2025
MBU modular wrappers               Luongo
pseudo-Mersenne modular folds      Schrottenloher
Montgomery generic-prime shell     Häner and Litinski
```

## Compatibility

- Litinski changes add-or-nothing into add-or-subtract; global corrections are mandatory.
- Gidney 2025 assumes a classical offset.
- Luongo changes cleanup, not the underlying arithmetic identity.
- Schrottenloher exploits the special form of the secp256k1 prime.
- Montgomery constructions change representation and wrapper.

## Benchmark priority

1. pseudo-Mersenne replay corrections;
2. classical constant/fold additions at peak;
3. controlled correction gates;
4. full multiplier only after output placement is solved.

The current main replay adder is already close to a quantum-quantum ripple floor, so the best new paper may target its correction shell rather than its central addition.
