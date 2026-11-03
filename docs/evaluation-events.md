# Evaluation display metrics

The trusted challenge evaluator supplies supplemental metrics in
`evaluation.completed` events:

```json
{
  "source": "evaluator",
  "kind": "evaluation.completed",
  "data": {
    "status": "ok",
    "score": 42,
    "metrics": {"throughput": 21, "latency_ms": 2.5}
  }
}
```

`metrics` maps display names to finite numbers. The CLI, transcript markers and
chart tooltips display these names and values without challenge-specific columns.
The primary `score`, status, budget accounting and verification remain separate.
Zero and negative metric values are supported. Strings, booleans, nested objects,
nulls and non-finite numbers are omitted. An explicit empty or malformed mapping
produces no supplemental metrics.

For historical events without `metrics`, readers display numeric fields outside
the standard event metadata. Scores, submission counters, durations and sequence
numbers are excluded from that fallback. Historical files are never rewritten,
and `dungeness evals --jsonl` preserves their original lines.

Challenge owners should emit the explicit map. During migration they can retain
flat fields for old consumers; new readers prefer the map and do not duplicate
those fields. OpenRSI owns its ECDSA metric names and emits both representations.
