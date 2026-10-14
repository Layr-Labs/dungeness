You are taking a closed-book source-familiarity audit.

Do not use tools, the filesystem, shell commands, web search, or external
sources. Answer only from knowledge already present in the model. Do not infer
an exact number or formula merely because the question suggests that one
exists. Say `unknown` when you do not remember a detail.

For each of the six papers below, answer the requested source-specific
questions and then assign your own confidence from 0 to 1.

1. Litinski, *Quantum schoolbook multiplication with fewer Toffoli gates*
   (arXiv:2410.00899v1)

   - What arithmetic operation replaces each shifted controlled addition?
   - State the paper's exact intermediate expression before the global
     corrections, and its reported total Toffoli count for the non-modular
     multiplier.
   - Give one important interface or representation limitation when importing
     the prime-modulus construction into an in-place canonical prime-field
     circuit.

2. Luongo et al., *Measurement-based uncomputation of quantum circuits for
   modular arithmetic* (arXiv:2407.20167v1)

   - Describe the two measurement branches of the one-bit MBU lemma and the
     condition on the repair computation.
   - Give the reported expected Toffoli costs of the Gidney modular adder and
     its controlled variant after MBU.
   - Which internal parts of controlled modular addition actually require the
     external control?

3. Gidney, *A Classical-Quantum Adder with Constant Workspace and Linear
   Gates* (arXiv:2507.23079v1)

   - Give the two principal workspace/Toffoli tradeoff points.
   - State the carry identity used for venting.
   - Why can an outer control be added without extra Toffolis in the paper's
     accounting?

4. Kornerup, Sadun, and Soloveichik, *Tight Bounds on the Spooky Pebble Game:
   Recycling Qubits with Measurements* (arXiv:2110.08973v3)

   - State the ghosting transformation and its distinct-label precondition.
   - Give the binomial relation connecting line length, pebbles, and the time
     parameter.
   - What memory resource remains live after the qubits are recycled?

5. Khattar et al., *Verifiable Quantum Advantage via Optimized DQI Circuits*
   (arXiv:2510.10967v1)

   - Distinguish explicit from implicit Bézout access in its reversible EEA.
   - How does the direct-division construction compute `A/B mod P` without
     materializing `B^-1`?
   - What does “Dialog” encode, and why do its quantitative results not
     directly transfer to integer arithmetic modulo a large prime?

6. Häner et al., *Improved quantum circuits for elliptic curve discrete
   logarithms* (IACR ePrint 2020/077)

   - How are the four Kaliski inversion cases normalized into a common round
     body?
   - How many fixed rounds are used, and how is the variable power-of-two
     pseudo-inverse correction integrated with cleanup?
   - Give one concrete producer/consumer or workspace-reuse optimization from
     the paper.

Return JSON conforming to the supplied schema. Keep each answer concise.
