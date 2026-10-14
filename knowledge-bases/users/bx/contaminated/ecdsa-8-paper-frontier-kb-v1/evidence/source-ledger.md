# Evidence ledger

## Primary papers

**[PAPER]**

1. André Schrottenloher, *Optimized Point Addition Circuits for Elliptic Curve
   Discrete Logarithms*, arXiv:2606.02235v1.
2. Daniel Litinski, *Quantum schoolbook multiplication with fewer Toffoli
   gates*, arXiv:2410.00899v1.
3. Alessandro Luongo, Antonio Michele Miti, Varun Narasimhachar, and Adithya
   Sireesh, *Measurement-based uncomputation of quantum circuits for modular
   arithmetic*, arXiv:2407.20167v1.
4. Craig Gidney, *A Classical-Quantum Adder with Constant Workspace and Linear
   Gates*, arXiv:2507.23079v1.
5. Niels Kornerup, Jonathan Sadun, and David Soloveichik, *Tight Bounds on the
   Spooky Pebble Game: Recycling Qubits with Measurements*,
   arXiv:2110.08973v3.
6. Han Luo et al., *Quantum Algorithm for Elliptic Curve Discrete Logarithms
   with Space-Efficient Point Addition*, arXiv:2607.13816v2.
7. Tanuj Khattar et al., *Verifiable Quantum Advantage via Optimized DQI
   Circuits*, arXiv:2510.10967v1.
8. Thomas Häner, Samuel Jaques, Michael Naehrig, Martin Roetteler, and Mathias
   Soeken, *Improved quantum circuits for elliptic curve discrete logarithms*,
   IACR ePrint 2020/077.

## Material represented

The dossiers use:

- compact binary-Euclid history and linear replay;
- controlled add-subtract and global correction algebra;
- one-bit measurement-based uncomputation;
- vented carries, carry-xor repair, and dirty borrowing;
- measured ghosts and time/space pebbling frontiers;
- explicit shared EEA state, active windows, and field-register demolition;
- synchronized EEA, Dialog state, and implicit division;
- integrated affine dataflow, adaptive uncomputation, and workspace reuse.

## Companion implementation evidence

**[CODE]** Companion artifacts supply examples of fixed schedules, compression,
truncated arithmetic, register layouts, and generated resource accounting.
These choices are evidence about implementations, not immutable requirements.

The question-first dossiers do not reproduce locally tuned companion parameters
as recommendations.

## Static benchmark contract

**[BENCHMARK]**

- quantum target coordinates and runtime-classical offset coordinates;
- affine secp256k1 point addition;
- all 9,024 deterministic circuit-seeded shots accepted;
- clean quantum ancillas, classical obligations, and relative phase;
- explicit forward/reverse correctness;
- average executed Toffoli times hard maximum qubit ID plus one.

## Deliberate omissions

This KB excludes:

- discoveries from later Astra runs;
- their recurrences, fused cells, schedules, or tuned constants;
- trusted-run rankings of the proposed dossiers;
- the live benchmark's current private implementation details;
- claims that an experiment has succeeded merely because it is suggested here.

The omission is intentional. This corpus is meant to test whether a
cross-paper decision structure can cause an agent to derive and validate deeper
research directions.
