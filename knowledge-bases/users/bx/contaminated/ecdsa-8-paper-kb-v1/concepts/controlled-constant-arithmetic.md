# Controlled constant arithmetic

The benchmark repeatedly adds or subtracts classical constants derived from:

- the secp256k1 modulus;
- pseudo-Mersenne fold constants;
- runtime classical offset coordinates;
- conditional modular corrections.

## Source options

```text
Gidney 2025  -> 3 or 4 Toffoli per bit with constant clean workspace
Litinski     -> add/subtract branch at ordinary-adder cost
Luongo       -> expected savings when uncomputing correction predicates
Schrottenloher -> modulus-specific short folds and truncated comparisons
Häner        -> controlled-copy plus uncontrolled-add pattern
```

## Decision rule

Classify the primitive first:

```text
known constant?
runtime classical bits?
quantum addend?
single quantum control?
carry-out retained?
exact or approximate reduction?
```

The cheapest construction changes with every answer.
