# syntax=docker/dockerfile:1
#
# prime-agent research-agent image. prime-agent (Prime Intellect) is a
# pi-mono derivative distributed as an npm package (pinned release tarball). Its
# RLM tools run in a Python kernel it builds with `uv` on first use -- that setup
# needs the internet, which the trial sandbox does NOT have. So we install uv and
# BAKE the kernel venv at build time (internet available), under a fixed HOME the
# adapter pins at runtime. Plus the pinned Rust toolchain for local build/test
# parity with the other agents.
FROM rust:1.93.0-bookworm AS rust

FROM node:22-bookworm-slim

# Fixed HOME so the baked prime-agent config + kernel venv sit at a stable,
# user-independent path the adapter re-pins at runtime (Harbor may exec as a
# different user). PI_OFFLINE/PI_SKIP_VERSION_CHECK (prime-agent reuses pi's env
# vars) disable startup network ops; PRIME_AGENT_INSTALL_UV lets install.sh use
# uv to build the kernel.
ENV HOME=/opt/prime-home \
    PRIME_AGENT_INSTALL_UV=1 \
    PI_OFFLINE=1 \
    PI_SKIP_VERSION_CHECK=1

# python3 runs the web/evaluate clients; git + g++ for parity; curl for the uv +
# prime-agent installers. Order matters: (1) $HOME must exist and (2) uv must be
# on PATH BEFORE the prime-agent installer, because install.sh builds the RLM's
# IPython kernel venv (uv-managed) at $HOME/.prime/agent/kernel-venv during
# install -- that step needs the internet, which the trial sandbox lacks, so we
# bake it here. (install.sh serves the current "stable" release, ~0.7.3; it is
# channel-pinned, not exact-version-pinned.) The kernel test fails the build if
# the venv did not get baked.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 ca-certificates git g++ curl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p "$HOME" \
    && curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh \
    && uv --version \
    && curl -fsSL https://app.primeintellect.ai/prime-agent/install.sh | sh \
    && prime-agent --version \
    && test -x "$HOME/.prime/agent/kernel-venv/bin/python" \
    && "$HOME/.prime/agent/kernel-venv/bin/python" -c "import ipykernel"

# Pinned Rust toolchain (1.93.0), copied from the official rust image so it
# matches the verifier/sidecar. CARGO_NET_OFFLINE forces runtime builds to use
# only the deps pre-fetched below (the sandbox has no network).
COPY --from=rust /usr/local/cargo /usr/local/cargo
COPY --from=rust /usr/local/rustup /usr/local/rustup
ENV CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    PATH=/usr/local/cargo/bin:$PATH \
    CARGO_NET_OFFLINE=true
RUN printf 'export PATH=/usr/local/cargo/bin:$PATH\n' > /etc/profile.d/rust.sh

# prime-agent config lives at $HOME/.prime/agent (same dir as the baked kernel).
# models.json overrides the openrouter provider's baseUrl to the gateway and
# upserts openai/gpt-5.6-sol with api "openai-responses" -- the same OpenRouter
# Responses path Codex and pi use. The placeholder OPENROUTER_API_KEY is
# forwarded by the adapter; the gateway swaps in the real key.
RUN printf '%s' \
        '{"providers":{"openrouter":{"baseUrl":"http://gateway:8080/model/openrouter/v1",' \
        '"models":[{"id":"openai/gpt-5.6-sol","name":"gpt-5.6-sol via OpenRouter","api":"openai-responses",' \
        '"reasoning":true,"input":["text"],"cost":{"input":5.0,"output":30.0,' \
        '"cacheRead":0.5,"cacheWrite":0.0},"contextWindow":272000,"maxTokens":64000}]}}}' \
        > "$HOME/.prime/agent/models.json" \
    && chmod -R 0777 "$HOME"

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
