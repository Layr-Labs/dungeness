# Retrieval query suite

This suite checks whether an agent can recover both curated guidance and source
detail. Queries are written as compact keyword sets suitable for the KB search
operation. A result is acceptable if it reaches the expected card/dossier or an
exact source page containing the answer.

## Schrottenloher

| Query | Expected answer route |
|---|---|
| `fixed tape 2.355n compression five Toffoli` | paper card; source page 10 |
| `binary Euclid b0 b1 swap subtract halve` | paper card; source page 9 |
| `replay double s conditional add swap` | paper card; source page 11 |
| `in-place multiplication convert transcript back x` | paper card; source page 12 |
| `x plus y equals q early empty iterations` | paper card; source pages 14–17 |
| `controlled modular adder 39 percent reconstruction 54` | paper card; source page 17 |

## Litinski

| Query | Expected answer route |
|---|---|
| `controlled add subtract n minus 1 no carry` | paper card; source page 1 |
| `2xy correction x plus 1 plus y divide by two` | paper card; source page 2 |
| `modular multiplication Montgomery garbage copy uncompute` | paper card; source page 2 |
| `ModMultStep 3 times 2 power w over 2` | paper card; source pages 3–4 |
| `prime multiplier n squared plus 6n window` | paper card; source page 4 |

## Luongo

| Query | Expected answer route |
|---|---|
| `modular adder CDKPM 8n n plus 3` | paper card; source page 26 |
| `hybrid modular adder 6n` | paper card; source page 27 |
| `only first addition final comparator controlled` | paper card; source page 28 |
| `measurement based uncomputation self adjoint half probability` | paper card; source pages 34–35 |
| `Gidney modular adder 3.5n expectation` | paper card; source page 36 |
| `controlled modular adder 4.5n plus 0.5` | paper card; source pages 38–39 |
| `two sided comparator 25 percent` | paper card; source pages 40–41 |

## Gidney

| Query | Expected answer route |
|---|---|
| `three clean ancilla 4n classical quantum adder` | paper card; source pages 1 and 7 |
| `two clean n minus 2 dirty 3n` | paper card; source pages 3–5 |
| `Z redundant carry complement sum identity` | paper card; source page 3 |
| `venting carries X basis phase task` | paper card; source pages 3–4 |
| `borrow bottom half top half five steps` | paper card; source page 7 |
| `controlled no additional Toffoli replace dk` | paper card; source pages 6–7 |

## Spooky Pebbling

| Query | Expected answer route |
|---|---|
| `ghost phase b dot y distinct x` | paper card; source pages 4–5 |
| `reuse register standard basis before unghost` | paper card; source page 5 |
| `classical bits total memory not reduced` | paper card; source pages 2 and 6 |
| `binomial m plus s minus 2 line pebbling` | paper card; source result pages |
| `irreversible pebbling s plus 1 O nT` | paper card; source page 20 |
| `binary tree h plus 1 O n log n` | paper card; source pages 21–22 |

## Luo

| Query | Expected answer route |
|---|---|
| `four phase EEA 6.316n exact bound` | paper card; source pages 11–13 |
| `r t invariant Work1 Work2 quotient split` | paper card; source pages 14–15 |
| `length registers location controlled active window` | paper card; source pages 14 and 20–29 |
| `IDiv measure Y phase b dot y recompute` | paper card; source pages 30–31 |
| `inversion 2n plus 6 log 19 qubits` | paper card; source page 32 |
| `256 inversion 30.59 point addition 70.10` | paper card; source page 35 |

## Khattar

| Query | Expected answer route |
|---|---|
| `explicit implicit Bezout transition matrix` | paper card; source pages 8–9 |
| `direct modular division apply transitions zero A` | paper card; source pages 9 and 11 |
| `in-register quotient unified cycle 6n iterations` | paper card; source pages 10–11 and 41–43 |
| `Dialog doubling inversion addition linear representation` | paper card; source pages 10–12 |
| `dialog length polynomial decreases one coefficient` | paper card; source pages 12–13 |
| `reference Python construct dialog modular division` | paper card; source pages 48–52 |

## Häner

| Query | Expected answer route |
|---|---|
| `constant addition curry copy classical constant` | paper card; source pages 4–5 |
| `Montgomery window lookup low bits divide by radix` | paper card; source pages 6–7 |
| `multiply then add pebbling one multiplication` | paper card; source page 7 |
| `Kaliski controlled swaps common round` | paper card; source pages 8–9 |
| `pseudo inverse correction reverse doubling` | paper card; source page 8 |
| `division reuse zero one modulus workspace` | paper card; source pages 8–10 |
| `projective non unique representation two C two D` | paper card; source pages 15–16 |

## Cross-paper decisions

| Query | Expected dossier |
|---|---|
| `branch tape versus Dialog information medium` | information location |
| `fixed exact recurrence probabilistic padding` | recurrence/state machine |
| `control boundary add subtract global correction` | arithmetic control |
| `canonical Montgomery representation conversion` | field representation |
| `fresh output demolition producer consumer` | output placement |
| `one bit carry full register ghost measurement scale` | measurement scale |
| `maximum referenced id weighted checkpoint` | space-time schedule |
| `prime polynomial field transfer barrier` | transfer barriers |
| `compact history active window composition` | cross-paper compositions |
| `paper implemented frontier reset untouched axis` | after the baseline |

## Acceptance target

- All paper-specific queries should retrieve the corresponding operational card
  or at least one linked source page.
- All cross-paper queries should retrieve the expected dossier.
- No query should require an upstream KB that is absent from this directory.
- A result that exposes only a headline count but not its contract is
  insufficient; descend to the paper card or source page.
