# Runtime verification

- Reused the synthetic problem, checkpoint schema, and offline evaluator interface. The fixture creates a committed local source and binds it to both the checkpoint and evaluator.
- Pinned the Workspace stock recovery adapter by commit and SHA-256. The loop reads a local copy and exercises its retry logic without reimplementing it.
- Built the gateway from the current source using a digest-checked local dependency image. This avoids Docker image pulls and package installation in Docker builds. The scored fixture replaces upstream destinations with loopback HTTPS and uses a synthetic credential.
- Kept the offline launcher fix in its own commit. The original tool resolver failed offline even with the Harbor wheel and transitive dependencies in the repository cache. Offline source runs now use the locked Harbor environment.
- The budget fixture settles a synthetic charge above the configured cap. The successful candidate remains available to the evaluator while the next inference attempt is rejected before dispatch.
- Colima maps host bind ownership to root in its Linux guest. The scratch fixture uses the Docker-reported owner while preserving gateway capability drops and the separate harness network. The product renderer keeps its host UID behavior.
- The Linux CI proof job requires an approved cache key and image ID. Keep the existing checks active until those inputs are provisioned.
- The unpatched Colima scored run failed when Compose waited for the gateway container. The scored evidence and PASS line report the gateway user override when it is applied.
- The scored fixture counts completed gateway HTTP events for model routes, including budget rejections. The usage summary retains the fixture's simulated charges.
- Timeout cleanup uses the Harbor trial names recorded under the scored run to remove only those Compose projects and their locally tagged images.
- The scored leg checks resources before recovery so a successful teardown cannot hide a product leak. Killing Harbor during verification reproduced a surviving verifier container. The loop tears down both projects by their recorded names and checks their exact Compose labels.
- The run record stores the fixture score in its Harbor execution statistics. The loop checks those statistics against Harbor's job result and compares the record's usage with the gateway summary.
- The full modes fail when the scored fixture uses a gateway user override. A standalone scored run reports the override and can still pass.
- The classic Docker builder left an unlabelled verifier image after Harbor was killed. The loop checks the fixture's exact Compose image tags as well as its project labels, and removes tags without deleting shared image references.
- Round 3 reproduced a green scored run that added a dangling provider image. The staged Dockerfiles now label every classic builder step after the base with a per-leg owner. Teardown removes tags before image IDs, deepest history first, and checks for new fixture images after removal.
- Scored cleanup checks both Harbor projects and removes new shared-memory staging only when it finds the synthetic credential. Post-command artifact validation records an evidence failure even when the command exited zero.
- A Colima build failed when the default bridge disappeared and left a labelled classic-builder container holding an image. The scored gateway build now uses no network, and fixture cleanup removes surviving containers with the exact owner label before removing images.
