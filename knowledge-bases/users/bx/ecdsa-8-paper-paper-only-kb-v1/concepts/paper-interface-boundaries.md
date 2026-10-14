# Paper interface boundaries

The most common cross-paper error is transferring an inner gate count without
its interface.

## Questions

1. Are operands classical, quantum, or mixed?
2. Is the output in place or fresh?
3. Which number representation is used?
4. What controls are quantum or classical?
5. What garbage remains?
6. How is phase repaired?
7. What must still be live during cleanup?
8. Is the claimed count fixed, expected, or asymptotic?
9. Which exceptional inputs are excluded?

## Rule

Use a source mechanism only after writing its complete state transformation
and cleanup transformation. A matching mathematical formula is insufficient.
