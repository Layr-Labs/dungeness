# Runtime verification

- Reused the synthetic problem, checkpoint schema, and offline evaluator interface. The fixture creates a committed local source and binds it to both the checkpoint and evaluator.
- Pinned the Workspace stock recovery adapter by commit and SHA-256. The loop reads a local copy and exercises its retry logic without reimplementing it.
- Built the gateway from the current source using a digest-checked local dependency image. This avoids Docker image pulls and package installation in Docker builds. The scored fixture replaces upstream destinations with loopback HTTPS and uses a synthetic credential.
- Kept the offline launcher fix in its own commit. The original tool resolver failed offline even with the Harbor wheel and transitive dependencies in the repository cache. Offline source runs now use the locked Harbor environment.
- The budget fixture settles a synthetic charge above the configured cap. The successful candidate remains available to the evaluator while the next inference attempt is rejected before dispatch.
- Colima maps host bind ownership to root in its Linux guest. The scratch fixture uses the Docker-reported owner while preserving gateway capability drops and the separate harness network. The product renderer keeps its host UID behavior.
- The Linux CI proof job requires an approved cache key and image ID. Keep the existing checks active until those inputs are provisioned.
