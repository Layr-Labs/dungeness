# Trusted runtime services

`gateway/` owns upstream model access, request policy and usage accounting.
These services run outside the untrusted harness; harness code must not supply
their credentials or implementation.

See [gateway architecture](DESIGN.md) and
[authentication](../docs/gateway-authentication.md).
