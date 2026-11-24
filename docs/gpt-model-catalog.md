# GPT model catalog

This is the text-model catalog bundled in this source revision, not live model
discovery or a promise of account entitlement. Every model below has an exact
`openai` and `openai-chatgpt` gateway route.
Use Responses for coding harnesses, including explicit tool and reasoning history.
Upstream account access still determines which model requests can succeed.

| Family | Model IDs |
| --- | --- |
| 6.2 | `gpt-6.2-astra`, `gpt-6.2-sol` |
| 6.1 | `gpt-6.1-sol`, `gpt-6.1-terra` |
| 6 | `gpt-6-astra`, `gpt-6-sol`, `gpt-6-luna` |
| 5.6 | `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna` |

These are explicit configured model IDs, not a Cartesian product of family and
tier names. Specialized image/audio/cyber models and internal Codex routing
identities are outside this text research-harness catalog.

All ten support `low`, `medium`, `high`, `xhigh`, and `max` reasoning effort.
`none` is also supported by 6.1 Terra, 6 Sol/Luna, and the three 5.6 models.
The selector should not offer `none` for either Astra, 6.2 Sol, or 6.1 Sol.

Reference prices and supported reasoning settings are pinned in
[`services/gateway/pricing.yaml`](../services/gateway/pricing.yaml). They are
comparison inputs, not live prices or an account's bill. Existing comparison
rates remain stable unless an operator explicitly changes the schedule. A run
retains the schedule it used. Extended cache retention and discounted/premium
execution are not qualified by this catalog. Subscription usage is normalized
for comparison, not reported as a per-token subscription charge.

The gateway tests check all ten IDs, both native provider routes, and exercise
new models with JSON/SSE tool history, exact accounting, and assigned-model
rejection. A platform bundling Dungeness must update and qualify its VM and
selector too. Adding only a dropdown option does not install gateway support.
