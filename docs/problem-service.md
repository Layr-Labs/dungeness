# Assigned problem service

A trusted task may define `problem_service: {context: problem-service, sha256: DIGEST}`.
The context is relative to the task and contains exactly `Dockerfile`, `server.py`,
and `task.json`. The compiler rejects escaping paths, symlinks, oversized files,
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
