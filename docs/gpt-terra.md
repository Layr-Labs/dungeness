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

Use the exact route/model entry in the bundled
[reference schedule](../services/gateway/pricing.yaml); the Terra versions have
different rates, including long-context tiers. These are pinned comparison
prices, not live billing quotes. Extended retention and discounted/premium tiers
remain unsupported. Image inputs are outside the current text-only gateway
contract. See the [request policy](gateway-request-policy.md).

This adds Dungeness gateway support. An enclosing platform with its own pricing
snapshot or model selector must add Terra there as well. A Mac VM that bundles
an older gateway/catalog still needs a qualified VM update before advertising
the model; this does not require changing the Mac application's executable.
