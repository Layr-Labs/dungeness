# Circuit-import checklist

Use this checklist before treating a paper component as a drop-in replacement.

1. **Value domain:** integer, residue, Montgomery residue, polynomial, or transition trace?
2. **Map shape:** in-place or out-of-place?
3. **Output semantics:** canonical, scaled, pseudo-inverse, or redundant?
4. **Garbage:** what remains, and how is it erased?
5. **Controls:** which operations need the caller’s control versus an internal predicate?
6. **Measurement:** what classical outcomes and phase obligations remain live?
7. **Workspace:** clean, dirty, quantum, and classical quantities?
8. **Cost convention:** exact, expected, asymptotic, or field-operation count?
9. **Lifetime coupling:** can a consumer use the result before producer cleanup?
10. **Failure model:** exact correctness, bounded approximation, or probabilistic branch cost?
11. **Conversion cost:** who enters and exits the paper’s representation?
12. **Verification:** which original source page establishes the imported claim?

Start with [representation and interfaces](representation-and-interface-contracts.md), then follow the linked atomic nodes.
