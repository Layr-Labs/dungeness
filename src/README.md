# Runtime implementation

`dungeness/compiler.py` resolves inputs and renders a run; `records.py` persists
evidence and source provenance; `scaffolds.py` materializes trusted starting files;
`execution/` launches and cleans up the run.
`evaluation_metrics.py` reads challenge-defined display values for the CLI and
transcript viewer. The root `dungeness` command connects these components.

See [development and boundaries](../docs/development.md).
