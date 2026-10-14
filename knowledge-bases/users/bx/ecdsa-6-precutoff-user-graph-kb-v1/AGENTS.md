# Using this quantum-arithmetic knowledge base

Use this knowledge base when a task involves multiplication, modular addition, controlled arithmetic, measurement-based uncomputation, carry cleanup, reversible EEA, modular inversion, Montgomery representation, or quantum/classical workspace tradeoffs.

## Mandatory retrieval checkpoints

Consult the KB:

1. after inspecting the target circuit and before selecting an arithmetic architecture;
2. before changing multiplication, modular addition, inversion, representation, cleanup, or controls;
3. after an unexplained correctness, phase, ancilla, or resource failure;
4. before declaring a paper mechanism incompatible;
5. before presenting a final resource comparison.

## Retrieval workflow

1. Search `index.md`, `manifest.json`, or `nodes.jsonl` using the concrete implementation problem.
2. Read two to five relevant files in `nodes/`.
3. Follow `related` IDs and the pages in `concepts/`.
4. Record which stable node IDs influenced the design.
5. Verify source pages from the node’s `Source` section before implementation.

## Evidence rules

- `PAPER`: directly supported by the cited paper and source location.
- Supported composition: component facts are established, but the combined end-to-end cost still needs proof.
- Architecture synthesis: a shared engineering abstraction derived across papers.
- Research hypothesis: not established by the cited papers.

Never present a synthesis or hypothesis as a paper result.

## Transfer rules

- Normalize representations before comparing costs.
- State in-place/out-of-place and canonical/scaled output contracts.
- Include garbage cleanup and representation conversion.
- Track measurement outcomes as live classical data and unresolved phase work.
- Separate caller controls from internal predicate controls.
- Do not transfer GF(2^b) arithmetic costs to large-prime integer arithmetic.
- Preserve producer/consumer lifetimes when estimating integrated savings.

## Final implementation report

Report:

- node IDs consulted;
- ideas used and rejected;
- representation and workspace assumptions;
- unresolved measurement or cleanup obligations;
- translated resource model;
- verification result in the target circuit.
