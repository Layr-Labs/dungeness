---
kind: node
id: paper-parameter-boundaries
source: arXiv:2606.02235v1
---

# Paper parameter boundaries

Schrottenloher's circuit uses fixed iteration, width, and comparison margins
to make an approximate construction static.

The paper-level relations are:

```text
Euclid iterations ~= 1.413n + O(sqrt(n))
compressed history ~= 2.355n + O(sqrt(n))
comparison windows << n where the error model permits
```

Concrete engineering constants outside the paper are intentionally absent
from this corpus.
