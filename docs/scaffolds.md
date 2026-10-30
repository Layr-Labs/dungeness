# Trusted scaffold preparation

Scaffolds are operator-owned inputs selected by the task, not the submitted
harness. Dungeness applies a data manifest; it never imports preparation code
from the task or harness on the host.

```yaml
schema_version: 2
type: scaffold
id: example
candidate_path: solution
candidate_files:
  blank/answer.txt: answer.txt
workspace_paths:
  - settings.txt
trusted_files:
  support/guide.txt: guide.txt
text_edits:
  - path: settings.txt
    pattern: PLACEHOLDER
    replacement: fixed
    matches: 1
```

Source file paths are relative to the manifest. Candidate destinations are
relative to `candidate_path`; trusted destinations and edit paths are relative
to the checked-out workspace. Paths cannot escape these roots. Trusted files
and edits must stay outside the candidate. Candidate initialization replaces
the previous candidate directory, leaving only the declared starting files.

Text edits use Python regular-expression substitution with DOTALL enabled.
Replacement strings follow `re.sub` escaping rules. Every edit must match the
declared positive count or compilation fails. The same trusted preparation is
applied to the agent workspace, intermediate evaluator and final verifier.
Source files, the manifest and edit paths are recorded in run provenance.

Consumers require `declarative-scaffolds-v2`. Schema-v1 scaffolds with implicit
Rust modules and validation stages are rejected. OpenRSI supplies the ECDSA
schema-v2 scaffold from its own problem package; generic Dungeness does not
bundle that challenge's starting candidate, SDK or source transformations.

`--fresh-start` without a scaffold creates empty candidate files/directories.
Use a scaffold when a language-specific entrypoint or support files are needed.
