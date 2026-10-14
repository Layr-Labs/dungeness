# Knowledge-base and experiment log

## [2026-08-31] ingest | Schrottenloher, arXiv:2606.02235

- Extracted the point-add schedule, fixed binary Euclid, compact history, Bézout replay, pseudo-Mersenne arithmetic, approximation parameters, and resource tables.
- Kept paper-v1 numbers separate from later companion-code numbers.

## [2026-09-02] ingest | Luo et al., arXiv:2607.13816v2

- Extracted the four-phase EEA, shared register layout, active windows, location-controlled primitives, measured field-register recycling, and resource tables.
- Recorded the 835-qubit / 70.10M-Toffoli point-add design and the implications for score product.

## [2026-09-08] ingest | six additional papers

- Litinski, arXiv:2410.00899: controlled add-subtract and schoolbook multiplication.
- Luongo et al., arXiv:2407.20167: formal MBU and modular-adder variants.
- Gidney, arXiv:2507.23079: constant-workspace classical adders and carry venting.
- Kornerup, Sadun, and Soloveichik, arXiv:2110.08973v3: spooky pebbling tradeoffs.
- Khattar et al., arXiv:2510.10967: explicit/implicit EEA and dialog representation.
- Häner et al., ePrint 2020/077: integrated ECDLP arithmetic and scheduling baseline.

## [2026-09-08] benchmark reconciliation | live ping-pong path

- Re-read the current point-add source and latest local memory notes at benchmark commit family `c1adf3e`.
- Replaced the obsolete assumption that the live path was the older jump-2 dialog/trailmix architecture.
- Recorded that replay/tape owns the peak and that generic checkpointing, radix-4 ping-pong, coefficient-growing Kaliski, Karatsuba-2 square, deeper walk, and uniform narrowing had unfavorable local results.
- Kept historical trusted scores as observations rather than constants because the source has continued to evolve.

## [2026-09-08] synthesis | unified eight-paper KB

- Consolidated all papers into one directory and one retrieval index.
- Preserved the earlier Schrottenloher and Luo concept decomposition.
- Added paper-level sections, atomic nodes, source records, cross-paper concepts, a mechanism matrix, and a ranked experiment map.
- Marked compatibility barriers explicitly: output placement, phase semantics, field model, lost history information, and current local floors.

## [2026-09-08] integration | Dungeness sidecar

- Imported the corpus as `knowledge-base:users/bx/contaminated/ecdsa-8-paper-kb-v1`.
- Preserved the existing one-paper and Luo-specific knowledge bases for historical run compatibility.
- Added read-only-sidecar logging guidance; run notes belong in `knowledge-base-notes/log.md`.
- Recorded the original imported tree digest in `knowledge-base.yaml`.

## Experiment template

```text
## [YYYY-MM-DD] experiment | title
- Base commit:
- Source mechanism:
- Target interval:
- Information-recovery argument:
- Files changed:
- Result:
- Score / executed Toffoli / qubits:
- Basis correctness:
- Phase and reverse correctness:
- Interpretation:
- Next action:
```
