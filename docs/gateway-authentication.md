# Gateway authentication

The harness sends inference in a supported wire protocol using its assigned
gateway URL and a placeholder credential. The gateway authenticates the upstream
connection using operator-owned configuration. Authentication does not translate
the request or choose research settings.

`services/gateway/gateway_auth.py` resolves authentication recipes. Recipes
specify headers whose values come from an environment variable, a field in a
credential JSON file, or a fixed value. An optional expiry source is checked
before request admission. The resolver has no provider-name branches and does
not use billing status to choose an authentication mechanism.

Built-in recipes live beside the provider destinations in `gateway_models.py`.
They preserve the existing environment names and credential-file mounts.
ChatGPT's recipe reads its access token and account ID from the staged file.
The older native-agent workflow has an explicit request-bearer fallback only
when no credential-file path is configured. A missing, malformed, or incomplete
configured file fails closed and never selects that fallback.

For compatible providers in `providers.json`, bearer substitution remains the
default. These optional fields configure different authentication headers:

```json
{
  "credential_env": "EXAMPLE_API_KEY",
  "credential_header": "x-api-key",
  "credential_prefix": "",
  "credential_headers": {
    "account-id": "EXAMPLE_API_KEY_ACCOUNT"
  }
}
```

This is a fragment of a complete trusted provider profile. Additional credential
variables must be namespaced under `credential_env` and must not collide with
other credentials or transport headers. Operators supply the corresponding
`TESTBED_EXAMPLE_API_KEY_ACCOUNT` variable; the compiler exposes it only to the
gateway, for a run that permits this provider. These fields are not a new
solver-controlled credential-grant format.

Session-token profiles require their existing `*_EXPIRES_AT` value. Credential
expiry does not trigger an API-key fallback or an automatic login/refresh.
Catalyst's local login readers remain responsible for extracting temporary
access from provider login files.

Trusted authentication headers override any allowed client metadata. Destinations
remain operator-controlled, redirects are not followed, and unknown providers
cannot borrow the default provider's credentials. The gateway does not log
resolved authentication values.

Usage parsing, pricing, allowed models, request restrictions, and budget
enforcement remain separate from authentication. Streaming requests still
request usage where required. The harness owns reasoning preferences.
