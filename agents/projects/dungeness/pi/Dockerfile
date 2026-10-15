# syntax=docker/dockerfile:1
#
# pi coding-agent image. Single stage on Node (pi is pure JS,
# no arch-specific native postinstall), plus the pinned Rust toolchain copied
# from the official rust image so the agent can build/test a Rust candidate
# locally (matching what the verifier compiles) -- same as the Codex/Claude
# images.
FROM rust:1.93.0-bookworm AS rust

FROM node:22-bookworm-slim@sha256:d649c27dae7ba0137b3cef5dd75baa422c08dc3d9e3fc0c23dfb172dc3cc6436

ARG PI_VERSION=0.73.1

# python3 runs the web/evaluate clients; git + g++ give parity with the other
# agents (git workflow, local C++ compile for world-map); curl matches what
# pi's own installer expects. Rust is added below. pi is installed GLOBALLY so
# the `pi` binary is on PATH: Harbor's pi adapter runs `. ~/.nvm/nvm.sh; pi ...`
# unconditionally, but the `;` means a missing nvm is non-fatal and the global
# `pi` still runs (we deliberately do NOT use nvm here, matching Codex/Claude).
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 ca-certificates git g++ curl \
    && rm -rf /var/lib/apt/lists/* \
    && npm install --global "@mariozechner/pi-coding-agent@${PI_VERSION}" \
    && pi --version

# Pinned Rust toolchain (1.93.0), copied from the official rust image so it
# exactly matches the verifier/sidecar. CARGO_NET_OFFLINE forces runtime builds
# to use only the deps pre-fetched below (the sandbox has no network).
COPY --from=rust /usr/local/cargo /usr/local/cargo
COPY --from=rust /usr/local/rustup /usr/local/rustup
ENV CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    PATH=/usr/local/cargo/bin:$PATH \
    CARGO_NET_OFFLINE=true
# Also expose cargo on login-shell PATH (the ENV above only covers non-login).
RUN printf 'export PATH=/usr/local/cargo/bin:$PATH\n' > /etc/profile.d/rust.sh

# pi configuration, baked into a fixed, user-independent dir. The gateway base
# URL lives here (pi reads no base-URL env var -- this models.json is the only
# mechanism, the pi analog of Codex's config.toml). We override the built-in
# "openrouter" provider's baseUrl to the gateway and upsert the pinned model by
# id so pi resolves it regardless of its bundled registry. The pinned model uses
# OpenRouter's OpenAI-compatible Responses API, so pi appends "/responses" to
# the base URL and calls /model/openrouter/v1/responses. The placeholder
# OPENROUTER_API_KEY (from compose) is forwarded by the adapter; the gateway
# swaps in the real key. PI_OFFLINE/SKIP_VERSION/TELEMETRY disable startup
# network ops (the sandbox has no egress); these must be image ENV because pi's
# adapter forwards only API-key env vars, not arbitrary ones.
ENV PI_CODING_AGENT_DIR=/opt/pi-agent \
    PI_OFFLINE=1 \
    PI_SKIP_VERSION_CHECK=1 \
    PI_TELEMETRY=0
RUN mkdir -p /opt/pi-agent \
    && printf '%s' \
        '{"providers":{"openrouter":{"baseUrl":"http://gateway:8080/model/openrouter/v1",' \
        '"models":[{"id":"openai/gpt-5.6-sol","name":"gpt-5.6-sol via OpenRouter",' \
        '"api":"openai-responses","reasoning":true,"input":["text"],' \
        '"cost":{"input":5.0,"output":30.0,' \
        '"cacheRead":0.5,"cacheWrite":0.0},"contextWindow":272000,"maxTokens":64000}]}}}' \
        > /opt/pi-agent/models.json \
    && chmod -R 0777 /opt/pi-agent

COPY workspace/ /workspace/repo/
COPY web_client.py /usr/local/bin/web
COPY evaluate.py /usr/local/bin/evaluate
COPY run_status.py /usr/local/bin/run-status
COPY candidate_state.py /usr/local/bin/candidate-state

# Pre-fetch crate deps if the workspace is a cargo project (ecdsa), so the agent
# can `cargo build --offline` at runtime; make CARGO_HOME writable for the agent.
RUN chmod 0555 /usr/local/bin/web /usr/local/bin/evaluate \
      /usr/local/bin/run-status \
      /usr/local/bin/candidate-state \
    && if [ -f /workspace/repo/Cargo.toml ]; then \
         (cd /workspace/repo && CARGO_NET_OFFLINE=false cargo fetch) \
         && chmod -R a+rwX /usr/local/cargo; \
       fi \
    && rustc --version

WORKDIR /workspace/repo

CMD ["/bin/bash"]
