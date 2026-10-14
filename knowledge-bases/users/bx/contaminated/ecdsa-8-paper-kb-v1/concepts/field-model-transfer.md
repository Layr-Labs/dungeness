# Field-model transfer

## Prime field

`ecdsa.fail` uses:

```text
Fp, p = 2^256 - 2^32 - 977
```

Addition needs carries and modular correction; multiplication can exploit pseudo-Mersenne folding.

## Binary extension field

Khattar's main EEA application uses `GF(2^b)`:

```text
addition = XOR
multiplication = polynomial multiplication/reduction
```

Its field-operation counts cannot be substituted for prime-field integer counts.

## Montgomery representation

Litinski and Häner prime-modulus multipliers use Montgomery form. Converting the live benchmark representation or mixing Montgomery and Solinas arithmetic adds wrapper costs and lifetime changes.

## Transfer rule

Only transfer:

- representation-independent schedule ideas;
- information-storage invariants;
- control/measurement identities whose predicate is rebuilt in the target field.

Re-price every arithmetic operation in the secp256k1 model.
