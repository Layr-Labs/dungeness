---
kind: node
id: khattar-prime-field-barriers
source: cross-paper analysis
depends_on: [khattar-dialog-representation, khattar-direct-division]
---

# Prime-field Dialog barriers

The paper's EEA acts on polynomials over `GF(2^b)`. Secp256k1 requires integer prime-field arithmetic.

Missing pieces:

- a compact integer transition alphabet;
- reversible quotient/sign extraction;
- bounded coefficient representation;
- prime-field replay arithmetic;
- proof that transition signs are encoded in retained state.

The polynomial-field Dialog does not itself prove that an integer recurrence
has a recoverable sign or quotient representation.
