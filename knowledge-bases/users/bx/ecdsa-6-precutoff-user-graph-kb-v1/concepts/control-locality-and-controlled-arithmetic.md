# Control locality and controlled arithmetic

A caller’s control rarely needs to be attached uniformly to every operation inside a modular-arithmetic block.

## Three control patterns

- [KB-LIT-01](../nodes/controlled-add-subtract.md): replace a shifted controlled add by a sign choice between add and subtract, then repair the aggregate offset.
- [KB-LUO-03](../nodes/external-control-scope.md): in controlled modular addition, only the first addition and final cleanup comparison need the external control.
- [KB-GID-03](../nodes/outer-control-at-zero-toffoli.md): for a classical offset, substitute the caller’s control for hardwired one-bits, adding no Toffolis in the paper’s model.

## Integration lesson

Separate:

1. caller control;
2. internally computed reduction or carry predicates;
3. fixed classical bits;
4. measurement-branch controls.

Controlling an entire compiled subcircuit can introduce unnecessary higher-controlled nonlinear gates. Derive control locality from the semantic condition each internal step must satisfy.
