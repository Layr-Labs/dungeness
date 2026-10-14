# Field-model transfer

## Integer prime fields

Schrottenloher, Luo, and Häner operate on integer residues modulo a prime.
Addition uses carries and canonical modular correction.

## Polynomial extension fields

Khattar's EEA developments use polynomials over a base field. Addition,
degree, shifts, and coefficient multiplication have different costs and
invariants from integer arithmetic.

## Montgomery representation

Litinski and Häner use Montgomery forms for generic-prime multiplication.
Entering or leaving that representation is a whole-shell decision.

## Transfer rule

Representation-independent ideas include:

- transition sequences;
- complementary growth and shrinkage;
- producer-consumer fusion;
- measurement and phase-repair identities.

Numerical operation counts remain attached to their original field model.
