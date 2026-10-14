---
kind: node
id: gidney-zero-overhead-control
source: arXiv:2507.23079
depends_on: [gidney-constant-workspace-adder]
---

# Zero-overhead control

**[PAPER]** To condition the constant addition on control `q`, replace the classical offset bits `d_k` by `q AND d_k`. Because `d_k` is classical, this changes control polarities and Clifford structure without adding Toffolis or workspace.

This applies when a classical offset is selected by one external control.
