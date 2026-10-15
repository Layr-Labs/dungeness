# syntax=docker/dockerfile:1
#
# Claude Code research-agent image. Single-stage for Claude Code itself
# (its npm postinstall fetches a native binary at build time -> ARCH-SPECIFIC),
# plus the pinned Rust toolchain copied from the verifier's base so the agent can
# build/test a Rust candidate locally (matching what the verifier compiles).
FROM rust:1.93.0-bookworm AS rust

FROM node:22-bookworm-slim@sha256:d649c27dae7ba0137b3cef5dd75baa422c08dc3d9e3fc0c23dfb172dc3cc6436

ARG CLAUDE_VERSION=2.1.259

# python3 runs the web/evaluate clients; git + g++ give parity with the Codex
# image (git workflow, local C++ compile for world-map). Rust is added below.
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 ca-certificates git g++ \
    && rm -rf /var/lib/apt/lists/* \
    && npm install --global "@anthropic-ai/claude-code@${CLAUDE_VERSION}" \
    && claude --version

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
