# Cross-paper mechanism map

This page reorganizes source-cited facts from the eight paper cards. It does
not add an application ranking.

## Information representations

| Representation | Stored information | Consumption rule | Source |
|---|---|---|---|
| Compressed binary-Euclid transcript | parity and comparison branches, compressed across triples | reverse linear coefficient updates | [Schrottenloher](paper-cards/01-schrottenloher.md) |
| Shared remainder/coefficient registers | shrinking remainders, growing coefficients, quotient segments, length metadata | location-controlled four-phase EEA | [Luo et al.](paper-cards/06-luo.md) |
| Dialog | sequence of small invertible polynomial transition symbols | apply transition product to another vector | [Khattar et al.](paper-cards/07-khattar.md) |
| Kaliski round state | normalized remainder/coefficient pairs and active-round controls | fixed-round subtract/add/halve/double body | [Häner et al.](paper-cards/08-haner.md) |

**[SYNTHESIS]** These are four distinct answers to the same abstract question:
where the information needed to reverse or reuse an Euclidean computation is
kept. The sources differ in field model, transition alphabet, metadata, and
consumer interface; their numerical resource claims are therefore not
interchangeable.

## Measurement-assisted cleanup

| Scale | Removed value | Retained obligation | Repair method | Source |
|---|---|---|---|---|
| one Boolean value | comparator or flag qubit | one measurement outcome | invoke a self-adjoint Boolean computation on one branch | [Luongo et al.](paper-cards/03-luongo.md) |
| carry stream | multiple carry qubits over time | classically indexed carry phases | carry-XOR recomputation with phase feed-forward | [Gidney](paper-cards/04-gidney.md) |
| arbitrary state block | a computational-basis checkpoint | measurement string | recreate the block, repair phase, uncompute | [Kornerup et al.](paper-cards/05-spooky-pebbling.md) |
| full field register | an obsolete field value | field-sized measurement string | reconstruct the value, apply dot-product phase, uncompute | [Luo et al.](paper-cards/06-luo.md) |

**[SYNTHESIS]** Measurement does not erase reversibility obligations. Each
source specifies what classical information survives and what computation
must later be available to repair phase.

## Multiplication interfaces

| Construction | Representation | Output placement | Cleanup feature | Source |
|---|---|---|---|---|
| Euclid transcript replay | canonical prime-field values | in place on one operand | reverse transcript construction | [Schrottenloher](paper-cards/01-schrottenloher.md) |
| signed schoolbook | binary integers | fresh `2n`-qubit product | global algebraic correction | [Litinski](paper-cards/02-litinski.md) |
| windowed Montgomery | Montgomery residues | fresh modular product | copy and reverse to remove window garbage | [Litinski](paper-cards/02-litinski.md) |
| add-and-halve Montgomery | Montgomery residues | integrated arithmetic workspace | consumer-aware uncomputation | [Häner et al.](paper-cards/08-haner.md) |
| exact EEA plus demolition | canonical prime-field values | in place with a third field register | full-register measurement and phase repair | [Luo et al.](paper-cards/06-luo.md) |

**[SYNTHESIS]** Gate counts cannot be compared without accounting for output
placement, persistent representation, garbage cleanup, and which registers
coexist.

## Controlled and constant arithmetic

| Mechanism | Main property | Source |
|---|---|---|
| Control only arithmetic boundaries implied by the modular dataflow | avoids controlling every internal operation | [Luongo et al.](paper-cards/03-luongo.md), [Häner et al.](paper-cards/08-haner.md) |
| Controlled add-subtract | makes the controlled primitive as cheap as an ordinary adder, followed by global correction | [Litinski](paper-cards/02-litinski.md) |
| Vented-carry constant addition | linear gates with constant clean workspace; outer control adds no Toffolis in the stated model | [Gidney](paper-cards/04-gidney.md) |
| Pseudo-Mersenne correction | replaces selected full-modulus corrections by arithmetic involving a short constant | [Schrottenloher](paper-cards/01-schrottenloher.md) |

## Time-space structure

**[EVIDENCE]** Spooky pebbling gives exact line-graph tradeoffs and general
conversion theorems for replacing stored checkpoints with measurement records
and later recomputation. See
[Kornerup et al.](paper-cards/05-spooky-pebbling.md).

**[EVIDENCE]** Schrottenloher identifies replay as the interval in which two
field values coexist with the compact transcript, while its forward and
reverse Euclidean phases have more spare workspace. See
[Schrottenloher](paper-cards/01-schrottenloher.md).

**[EVIDENCE]** Häner et al. show a smaller-scale form of lifetime scheduling by
keeping a producer's workspace through its sole consumer and reversing the
producer afterward. See
[Häner et al.](paper-cards/08-haner.md).

**[SYNTHESIS]** The three sources operate at different granularities:
whole dependency graphs, phase-level register lifetimes, and individual
producer-consumer pairs.
