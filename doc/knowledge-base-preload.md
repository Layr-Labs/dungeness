# Run-Scoped Knowledge Bases

Dungeness serves each versioned knowledge base from a read-only, no-egress
sidecar. The corpus is not copied into the graded candidate workspace.

## Agent interface

```text
knowledge-base status
knowledge-base list
knowledge-base search "<query>" [--max-results N] [--context-lines N]
knowledge-base read <relative-page>
knowledge-base neighbors <node-id-or-page>
knowledge-base inspire --search-id <id> \
  --passage relative/page.md:L10-L18 \
  --takeaway "<implementation idea>" \
  --planned-change "<candidate change>"
```

The sidecar exposes matching HTTP endpoints under `/v1`, including
`POST /v1/inspire`. Search uses `ripgrep` with an argument array, a fixed
corpus root, bounded passages, relative paths, and stable line ranges.

Those are the default capabilities for existing curated Markdown corpora.
A manifest can narrow the interface:

```yaml
interface:
  mode: raw-document-read-only-v1
  operations:
    - read
```

The compiler passes the resolved operation list to the agent client, and the
sidecar independently enforces it. Disabled operations are neither advertised
by the client nor accepted by the service.

## Raw paper treatments

The `raw-document-read-only-v1` treatment stores one original paper artifact
without summaries, semantic chunks, indexes, annotations, companion code, or
generated orientation pages. For a PDF,
`knowledge-base read <paper.pdf> --pages 1-5` runs `pdftotext -layout` inside
the sidecar at request time and returns that inclusive page window. Reading
successive windows covers the complete paper without risking shell-output
truncation. Page boundaries come from the original PDF; this conversion is
transport rendering, not a persisted preprocessed corpus, and the copied
source PDF remains byte-for-byte unchanged.

Only `read` is enabled. Status, listing, search, graph traversal, and
inspiration attribution return a forbidden response. The read event is still
sent to the gateway's canonical event collector and records both the source
artifact hash and rendered-content hash.

Example:

```yaml
initialization:
  knowledge_base:
    ref: knowledge-base:users/bx/ecdsa-schrottenloher-raw-paper-v1
    access: sidecar
    prompt_profile: knowledge-base-prompt-profile:system/dungeness/raw-paper-read-only-v1
    layers:
      - raw_paper
    behavior_feedback:
      enabled: false
      mode: off
```

The `raw-document-corpus-read-only-v1` treatment applies the same contract to
multiple original PDFs. Each source document records its immutable hash and
page count in `source.documents`; the prompt profile renders a deterministic
five-page-window read plan covering every paper. The sidecar still exposes only
`read`, and it creates no generated index, summaries, semantic chunks, or
companion-code projection.

Example:

```yaml
initialization:
  knowledge_base:
    ref: knowledge-base:users/bx/ecdsa-8-raw-paper-kb-v1
    access: sidecar
    prompt_profile: knowledge-base-prompt-profile:system/dungeness/raw-paper-corpus-read-only-v1
    layers:
      - raw_papers
    behavior_feedback:
      enabled: false
      mode: off
```

Search has one behavior and no modes. The query is split on whitespace, every
term is matched as a case-insensitive literal substring (`--fixed-strings`, so
punctuation and regex metacharacters are never special), terms are OR'd, and
passages are ranked by how many distinct terms they contain. A multi-term query
therefore always returns the pages that mention some of the terms rather than
returning nothing because one term was absent.

Equally good matches are ordered so qualifying sources come before orientation
pages, and every result carries `qualifying_source`, so the agent can see which
passages can carry a qualifying lookup before spending one. A rejected
`inspire` returns `qualifying_sources`, the prefixes and pages that would have
qualified.

## Behavior feedback

The knowledge base is an inspiration source, not a completion gate or search
quota.

A lookup qualifies only when the agent:

1. searches with a non-empty query and receives results;
2. selects an exact returned passage not previously used by a qualifying
   lookup;
3. records a concrete implementation takeaway; and
4. records the planned candidate change.

For the ECDSA corpus, a manifest-level qualifying-source filter requires an
atomic node or the companion-code map. Reading only generic orientation or
hypotheses does not qualify. This closes the observed gap where an agent could
confirm a high-level strategy without retrieving code-level evidence that
could guide the implementation.

The next valid LM evaluation after a qualifying lookup is attributed to that
inspiration cycle:

- If the score establishes a new lower best, the next agent context receives
  a specific carrot message with the query, takeaway, planned change, and
  score improvement.
- If it does not improve, no carrot is awarded.
- After three consecutive no-progress evaluations without a qualifying
  lookup, the next context receives a specific stick message directing the
  agent to seek a different KB idea.

The first valid score establishes the baseline. Failed evaluations do not
advance counters. The controller never changes the evaluator score.

## Feedback delivery and telemetry

The research-state controller owns attribution and counters. The gateway
injects visible feedback before the agent's next action as runtime-generated
`<behavior_feedback>` context.

Events are written to:

```text
usage/events.jsonl
```

The canonical stream distinguishes `knowledge-base`, `research-state`, and
`gateway` sources and semantic event kinds.

## Run-spec configuration

```yaml
initialization:
  knowledge_base:
    ref: knowledge-base:users/bx/contaminated/ecdsa-paper-kb-v1
    access: sidecar
    prompt_profile: knowledge-base-prompt-profile:system/dungeness/ecdsa-paper-v1
    layers:
      - paper_knowledge_base
    behavior_feedback:
      enabled: true
      mode: visible
      minimum_improvement: 0
      kb_attribution_window_evaluations: 1
      no_progress_evaluations: 3
      expose_pre_stick_counter: true
```

`mode` accepts `off`, `shadow`, or `visible`. Web-search and evaluation
controls remain independent.
