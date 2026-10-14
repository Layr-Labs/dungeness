# Standard ECDSA legacy + KB v1 run

This directory defines the canonical regression run with:

- Codex `0.148.0`;
- the direct OpenAI API route using `gpt-5.6-sol`;
- xhigh reasoning effort with detailed summaries;
- the neutral `ecdsa-fail-performance-reconstruction` task description;
- legacy code from checkpoint `62ae3d00d1e01d7bc640b5163cfea8dabffd8392`;
- `ecdsa-paper-kb-v1` through the knowledge-base sidecar;
- web search disabled;
- iterative evaluation; and
- a `$12` model-cost limit.

Run it with:

```bash
./dungeness run \
  run-specs/users/bx/ecdsa-standard-codex-openai-gpt56-kb-v1-legacy-12usd/ecdsa-standard-codex-openai-gpt56-kb-v1-legacy-12usd.yaml
```

Treat changes to any listed dimension as a new standard version rather than
silently changing this baseline.
