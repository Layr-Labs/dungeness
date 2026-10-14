# Coverage matrix

## Corpus integrity

| Measure | Value |
|---|---:|
| Source PDFs | 8 / 8 |
| Searchable PDF pages | 227 / 227 |
| Extracted source words | approximately 104,166 |
| Operational paper cards | 8 |
| Cross-paper decision dossiers | 10 |
| Raw PDF fallback | present for every source |
| Prior Astra discoveries included | none |

PDF SHA-256 hashes, per-paper page counts, and per-page word counts are stored
in
[`source-page-manifest.json`](../source-pages/source-page-manifest.json).

The Markdown extraction is complete by PDF page count, but text extraction can
lose equation layout, circuit wiring, subscripts, or figure geometry. The raw
PDF is authoritative whenever formatting matters.

## Paper-to-curation coverage

| Paper | Source pages | Operationally curated ranges | Material retained only in source fallback |
|---|---:|---|---|
| Schrottenloher | 19 | point addition 6–8; EEA/history/replay 9–12; arithmetic 13–17 | introduction, comparisons, concluding resource context, references |
| Litinski | 6 | complete technical argument 1–5 | circuit figure page and references remain searchable |
| Luongo | 45 | modular adders 24–34; MBU and applications 34–41 | arithmetic preliminaries, alternative adder proofs, appendices/references |
| Gidney | 8 | complete construction 1–7 | acknowledgments and references |
| Spooky Pebbling | 25 | model/ghosting 1–7; line results 8–19; DAG/tree 19–22 | detailed proofs and references not repeated in dossiers |
| Luo | 50 | EEA framework/layout 10–19; active windows/circuits 20–29; point addition/resources 30–36 | preliminaries, full proofs, appendices, code/resource details |
| Khattar | 52 | EEA/Dialog 8–15; cycle proof 41–43; reference implementations 48–52 | DQI algorithm, coding theory, long appendices outside EEA relevance |
| Häner | 22 | arithmetic 4–7; inversion/division/point shell 8–12; coordinate/window analysis 15–18; resources 19–22 | introductory context and intermediate appendices remain searchable |

“Retained only in source fallback” does not mean removed. Every listed page is
present under `source-pages/`, and every original PDF is present under `raw/`.
It means the material was not duplicated into a curated paper card because it
is peripheral to this benchmark or already represented by a narrower evidence
route.

## Architectural coverage

| Question | Schrottenloher | Litinski | Luongo | Gidney | Spooky | Luo | Khattar | Häner |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Complete affine shell | strong | — | — | — | — | strong | — | strong |
| In-place multiplication/division | strong | — | — | — | — | strong | implicit analogue | division shell |
| Fresh-output multiplication | — | strong | — | — | — | wrapper consumes | — | strong |
| EEA recurrence | binary | — | — | — | schedule only | four-phase | synchronized/Dialog | Kaliski |
| History/information representation | packed tape | correction state | flag | phase tasks | ghosts | shared state | Dialog | active round state |
| Prime-field reduction | pseudo-Mersenne | Montgomery | generic modular | wrapper needed | — | generic prime | transfer needed | Montgomery |
| Controlled arithmetic | strong | add-subtract | structural proof | constant offset | — | location controls | transition controls | strong |
| Measurement cleanup | local | lookup cleanup dependency | one-bit MBU | carry venting | global model | full word | — | AND/lookup techniques |
| Space scheduling | register sharing | fresh accumulator | ancilla portfolio | dirty borrowing | pebbling | active windows/sharing | coefficient sharing | pebbling/reuse |
| Exactness alternatives | approximate margins | exact local arithmetic | expected cost | exact with measurement | exact model | exact EEA | exact polynomial | exact architecture |

## Evidence-card completeness criteria

Each operational card is required to include:

- source and role;
- primitive or state-machine input/output contract;
- information retained and discarded;
- forward sequence;
- cleanup, inverse, or phase-repair path;
- workspace shape;
- cost model and headline formulas where relevant;
- exceptional cases or approximation assumptions;
- transfer barriers;
- at least one smallest experiment;
- direct page-level evidence links.

The cards satisfy these criteria at different lengths according to the source's
relevance. The full source page remains available whenever a card omits a proof
or secondary construction.

## Intentional exclusions

The curated layers do not contain:

- discoveries, scores, or tuned constants from previous Astra runs;
- an assertion that any paper is globally optimal;
- a preselected winning cross-paper composition;
- source claims converted silently between T, Toffoli, T-depth, logical width,
  and the benchmark objective;
- polynomial-field resource counts presented as secp256k1 counts;
- measurement savings without their classical outcomes and phase repair.

These exclusions preserve the experiment: the KB supplies published evidence
and research structure without leaking a prior run's answer.

## Known extraction risks

1. Equations may have spacing or superscript damage.
2. Circuit figures are represented mainly by nearby captions and extracted
   labels.
3. Multi-column reading order may be imperfect.
4. Printed page numbers may differ from PDF page numbers.
5. Source links in cards use PDF page numbers.

When a retrieved passage depends on layout, read the raw PDF linked from
[`evidence/source-index.md`](../evidence/source-index.md).
