# Model access: terms and boundaries

Use **access route** for a supported way to call a model service. Describe the
service and authentication method explicitly: **OpenAI API — API key** or
**ChatGPT Codex — account access**. A vendor name alone does not identify the route.

The existing configuration field `provider` and IDs such as `openai` are
historical access-route selectors. They remain valid for compatibility. In prose,
**provider** means the organization operating the upstream service.

## Terms

| Term | Meaning |
| --- | --- |
| Model | The model requested through an access route, including any trusted alias mapping. |
| Harness | The agent program making requests: its loop, prompts, tools and memory. |
| Provider | The organization operating the upstream service, such as OpenAI, Anthropic or Google. An aggregator may serve models from other organizations. |
| Service | The particular upstream product/API, such as the OpenAI API or ChatGPT Codex backend. |
| Access route | A supported service, protocol, authentication recipe and trusted routing rules. The registry also associates model mappings and usage interpretation with it. |
| Protocol | The request, response, streaming and tool-call format understood by both sides. |
| Account | The upstream identity whose access or quota is used. Project or organization context may further select the resources or billing arrangement. |
| Credential | Authorization material, such as an API key or access token. Protect credential documents as secrets even when they also contain public account metadata. |
| Credential source | Where the trusted runtime obtains credentials: for example, a selected local login file, keychain entry or supplied key. |
| Credential resolver | Code that obtains credentials from the selected source, validates the required fields and prepares them privately for a run. The gateway checks recipe-declared expiry when admitting requests. |
| Authentication recipe | Trusted instructions for applying credentials to an upstream request, such as constructing an authorization header and required account metadata. |
| Usage policy | The rules for measuring usage, applying reference prices and enforcing run budgets. |
| Gateway | The trusted component that mediates model requests, applies authentication and enforces the run's access and usage policies. |

These are responsibilities and data, not a list of separately deployed services.
A credential resolver does not always read a local login. A hosted store could
be another source in a future implementation; this document does not add one.
Current expiry and refresh behavior is described in
[gateway authentication](gateway-authentication.md).

## How the terms fit together

```text
Run selects: harness + model + access route + account/source + limits

Credential source -> resolver -> private run credentials
                                         |
Harness -> gateway (route + authentication recipe + usage policy) -> service
```

This is a conceptual flow, not a new run-spec schema. The harness receives the
assigned gateway URL and placeholder credentials. Real credentials belong to the
trusted side of the run.

Account entitlement, upstream billing and normalized experiment cost are distinct.
The access route does not guarantee a subscription plan or model entitlement;
the upstream determines those from the account and request context. The usage
policy records reference cost separately from actual charges.

A complete research run also has a problem and evaluator, execution environment,
resource limits and evidence. Those belong to the run contract rather than the
credential resolver. Model access alone does not establish execution attestation
or prove which model the upstream actually executed.

## Existing selectors

The [access-route table](gateway-authentication.md#llm-access-routes) maps readable
names to the unchanged `provider` IDs. `dungeness providers` reports those IDs for
compatibility checks. Discovery establishes implementation availability only:
it does not test an account, perform inference or establish attested-run support.

See [integrating model access](integrating-model-access.md) for the solver-agent
handoff, detailed input discovery and trusted credential-preparation interface.
