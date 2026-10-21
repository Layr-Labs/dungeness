# Assigned problem service

A trusted task may define `problem_service: {context: problem-service, sha256: DIGEST}`.
The context is relative to the task and contains exactly `Dockerfile`, `server.py`,
and `task.json`, plus an optional `files` directory of declared attachments.
The compiler rejects escaping paths, symlinks, oversized files,
and documents that do not match the assigned SHA-256.

Dungeness starts this service on a private internal network shared only with the
gateway. It has a read-only filesystem, no host ports, no provider credentials,
and a read-only task-document mount. The gateway exposes `GET /task`, fetching
only `http://problem:8091/task` and checking the digest again. It rejects request
selectors, redirects, oversized documents, and hash mismatches. The main agent
receives `DUNGENESS_PROBLEM_URL=http://gateway:8080/task`.

The digest uses UTF-8 JSON with sorted keys, compact separators, non-ASCII
characters preserved, and non-finite numbers rejected. Version 1 documents have
`schema_version: 1`; the challenge defines the remaining task fields and owns
its statement and server implementation. The service must also expose `/healthz`.
This endpoint never executes candidate code. Verification stays independent.
Tasks without `problem_service` keep their existing behavior.

## Versioned resources

Task attachments declare `name`, `bytes`, `sha256`, and `media_type`. The gateway
serves them at `/task/files/<name>` only after checking the complete response's
size and hash. Media types are not restricted to PDF or JSON: Markdown, CSV, code,
archives and other formats use the same pinned transport. Responses include
`Content-Type`, `X-Content-SHA256`, `Content-Disposition: attachment`, and
`X-Content-Type-Options: nosniff`. Limits remain 64 attachments, 32 MiB each, and
256 MiB total.

An attachment may also declare a `paths` array with semantic aliases:

```json
{
  "name": "notes.md",
  "bytes": 8,
  "sha256": "<sha256-of-exact-bytes>",
  "media_type": "text/markdown",
  "paths": ["/ecdsa-fail/v1/resources/notes", "/ecdsa-fail/resources/notes"]
}
```

The gateway recognizes `/<slug>/<release>/description`,
`/<slug>/<release>/knowledge-base`, and `/<slug>/<release>/resources/<id>`, plus
their unversioned forms. Each URL must match an explicit path in the run's pinned
task document. Unversioned paths select the assigned release, never a mutable
global latest release. Unknown paths/releases return 404 and query selectors are
rejected. Upstream requests still use only `/task` and `/task/files/<name>` on the
assigned internal problem service, without forwarding caller credentials.

The challenge owns the human-readable release tag and format-neutral catalog
schema. Dungeness neither downloads arbitrary catalog URLs nor exposes a public
knowledge-base service. Existing tasks without these path declarations continue
to use their original URLs.
