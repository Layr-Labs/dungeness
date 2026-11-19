# GPT model catalog

General-purpose GPT models from 5.6 onward, audited on 2026-11-18 against
[OpenAI's model catalog](https://developers.openai.com/api/docs/models).
Every model below has an exact `openai` and `openai-chatgpt` gateway route.
Use Responses for coding harnesses, including explicit tool and reasoning history.
Upstream account access still determines which model requests can succeed.

| Family | Model IDs |
| --- | --- |
| 6.2 | `gpt-6.2-astra`, `gpt-6.2-sol` |
| 6.1 | `gpt-6.1-sol`, `gpt-6.1-terra` |
| 6 | `gpt-6-astra`, `gpt-6-sol`, `gpt-6-luna` |
| 5.6 | `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna` |

These are explicit published model IDs, not a Cartesian product of family and
tier names. Specialized image/audio/cyber models and internal Codex routing
identities are outside this text research-harness catalog.

All ten support `low`, `medium`, `high`, `xhigh`, and `max` reasoning effort.
`none` is also supported by 6.1 Terra, 6 Sol/Luna, and the three 5.6 models.
The selector should not offer `none` for either Astra, 6.2 Sol, or 6.1 Sol.

Prices are pinned in `services/gateway/pricing.yaml`. New entries use Standard
text input, cache read/write, output and whole-request long-context rates from
each model's official page at `/api/docs/models/<model-id>`. Extended cache
retention and discounted/premium execution are not qualified by this catalog.
Subscription runs use normalized comparison cost, not an actual per-token
subscription bill. Existing reference prices are preserved: the historical
GPT-5.6 Sol $5/$30 input/output comparison rate is not replaced by its temporary
$4/$20 promotion, which the official page currently lists through 2026-11-30.

The gateway tests check all ten IDs, both native provider routes, and exercise
new models with JSON/SSE tool history, exact accounting, and assigned-model
rejection. A platform bundling Dungeness must update and qualify its VM and
selector too. Adding only a dropdown option does not install gateway support.
