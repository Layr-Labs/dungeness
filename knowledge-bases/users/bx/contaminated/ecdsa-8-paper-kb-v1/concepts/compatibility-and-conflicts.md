# Compatibility and conflicts

## Strongly compatible

- Schrottenloher history/replay and pseudo-Mersenne arithmetic with current ping-pong.
- Gidney constant adders with classical correction hotspots.
- Luongo MBU with one-bit flags if dynamic semantics pass.
- Häner lifetime fusion with any arithmetic architecture.

## Conditionally compatible

- Luo register demolition if the complete old value is exactly recomputable.
- Spooky ghosting if checkpoint reconstruction is cheaper than retained peak width.
- Khattar Dialog if prime-field transitions and sign recovery are proved.
- Litinski add-subtract if corrections fuse into the surrounding cell.

## Direct conflicts

```text
Litinski fresh product register
vs current in-place peak-sensitive interface

Khattar GF(2^b) operation counts
vs secp256k1 prime-field arithmetic

mechanical reverse of MBU
vs explicit dynamic-circuit inverse

deleting sign tape
vs information-theoretic sign loss

generic Bennett checkpointing
vs measured current product economics
```

## Safe hybrid rule

Import the smallest mechanism whose input/output contract already matches. Architectural hybridization should follow a written state/lifetime proof.
