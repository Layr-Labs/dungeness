# Knowledge belongs to the harness

Dungeness no longer supplies a knowledge-base service, lookup client, prompt
profile or read hooks. An agent owns its documents, memory, indexes, retrieval
code and prompting. Bundle them into the agent image and use ordinary local
files, libraries or child processes. No knowledge manifest or approved file
format is required.

## Migration

1. Copy the files your old knowledge manifest selected into your harness source.
   Keep the original documents and any attribution or licenses you need.
2. Include those files and retrieval dependencies in the harness image. For
   example, `COPY . /opt/harness/` includes a harness's source, PDFs and local
   databases together. A Dungeness agent Dockerfile may use that prebuilt image
   as its `FROM` image before adding the task workspace and runtime clients.
3. Replace `knowledge-base read/search/...` calls with your own reader/retriever.
   Put research instructions and memory policies in the harness.
4. Remove `initialization.knowledge_base` from the run spec. New runs explicitly
   reject that setting, including null/empty values, so knowledge is never
   silently discarded.

Historical `knowledge-bases/` corpora and run/experiment records are retained as
source material. They are not loaded by the current runtime and are excluded
from runtime distributions. Replay an old experiment using its recorded source
revision, which retains its original services and behavior.

The model gateway still meters declared model calls. Agent-owned retrieval that
uses a model must use that same gateway; bundling knowledge does not add internet
access or allow bypassing accounting. The task, candidate paths and trusted
verifier remain controlled by the platform.
