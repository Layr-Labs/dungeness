# GPT Terra

Select `gpt-6.1-terra` through `openai` for API access or `openai-chatgpt`
for local ChatGPT access. The existing gateway protects credentials, enforces
the assigned model allowlist and accounts for each completed request.
Account entitlement is determined by the upstream service.

`gpt-5.6-terra` is also supported on both routes. Keep the exact version in the
request and run record; the two Terra versions have different reference prices.

Use the Responses API for a coding harness: Terra's tool calls require it.
For a Dungeness command run:

```yaml
model_access:
  models:
    - provider: openai
      upstream_id: openai/gpt-6.1-terra
      request_model: gpt-6.1-terra
      api: openai-responses
      name_format: request
```

Use `TESTBED_OPENAI_API_KEY` for the API route. For ChatGPT access, change the
provider to `openai-chatgpt` and use the private `DUNGENESS_CODEX_AUTH_FILE`
described in [command harnesses](command-harness.md). The harness reads its
assigned gateway URL from `DUNGENESS_TASK`; it must not read the credential.

In the request, `reasoning.effort` can be `none`, `low`, `medium`, `high`,
`xhigh` or `max`. Keep encrypted reasoning history intact across tool calls.

The bundled standard text reference, checked on 2026-11-18, charges per million
tokens: $1 input, $0.05 cache read, $1.25 cache write and $5 output. Above 272,000
input tokens the full request uses $2, $0.10, $2.50 and $7.50 respectively.
These cache-write rates apply to standard 30-minute retention. Extended
retention, discounted/background execution and premium service tiers remain
unsupported. ChatGPT usage uses normalized cost, not a fabricated subscription
cash charge. Image inputs remain unsupported by the current gateway.

Source: [OpenAI's GPT-6.1 Terra model reference](https://developers.openai.com/api/docs/models/gpt-6.1-terra).

GPT-5.6 Terra's Standard text reference is $2 input, $0.20 cache read,
$2.50 cache write and $12 output per million tokens. Above 272,000 input tokens,
the full request uses $4, $0.40, $5 and $18 respectively. Source:
[OpenAI's GPT-5.6 Terra model reference](https://developers.openai.com/api/docs/models/gpt-5.6-terra),
checked 2026-11-18.

This adds Dungeness gateway support. An enclosing platform with its own pricing
snapshot or model selector must add Terra there as well. A Mac VM that bundles
an older gateway/catalog still needs a qualified VM update before advertising
the model; this does not require changing the Mac application's executable.
