FROM node:22-bookworm-slim@sha256:d649c27dae7ba0137b3cef5dd75baa422c08dc3d9e3fc0c23dfb172dc3cc6436 AS codex

ARG CODEX_VERSION=0.148.0

# Install while the image is being built. At trial time the main container is
# deliberately attached only to an internal Docker network, so Harbor cannot
# download an installed agent after startup.
RUN npm install --global "@openai/codex@${CODEX_VERSION}" \
    && codex --version

# Source of the pinned Rust toolchain (matches the verifier/sidecar).
FROM rust:1.93.0-bookworm AS rust

FROM gcc:14-bookworm@sha256:5e927c284bf55a7dc796262e311a0703344f62f41f5621eb56843111b1d37e15

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ripgrep \
    && rm -rf /var/lib/apt/lists/*

# Codex's npm launcher needs Node, the main package, and a platform-specific
# native package installed beside it under the @openai scope. Copying the whole
# scope preserves that pair without adding npm or package-manager state to the
# runtime image.
COPY --from=codex /usr/local/bin/node /usr/local/bin/node
COPY --from=codex /usr/local/lib/node_modules/@openai /usr/local/lib/node_modules/@openai

# Pinned Rust toolchain (1.93.0) so the agent can build/test a Rust candidate
# locally, matching the verifier. CARGO_NET_OFFLINE forces runtime builds to use
# only the deps pre-fetched below (the sandbox has no network).
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
COPY research_worker.py /usr/local/bin/research-worker
COPY run_status.py /usr/local/bin/run-status
COPY candidate_state.py /usr/local/bin/candidate-state
COPY knowledge_base.py /usr/local/bin/knowledge-base
COPY research_state_hook.py /usr/local/bin/research-state-hook

RUN ln -s ../lib/node_modules/@openai/codex/bin/codex.js /usr/local/bin/codex \
    && chmod 0555 /usr/local/bin/web /usr/local/bin/evaluate \
      /usr/local/bin/research-worker \
      /usr/local/bin/run-status /usr/local/bin/candidate-state \
      /usr/local/bin/knowledge-base \
      /usr/local/bin/research-state-hook \
    && codex --version \
    && if [ -f /workspace/repo/Cargo.toml ]; then \
         (cd /workspace/repo && CARGO_NET_OFFLINE=false cargo fetch) \
         && chmod -R a+rwX /usr/local/cargo; \
       fi \
    && rustc --version

WORKDIR /workspace/repo

CMD ["/bin/bash"]
