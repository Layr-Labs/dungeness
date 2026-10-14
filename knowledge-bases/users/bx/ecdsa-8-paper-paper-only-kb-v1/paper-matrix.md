# Paper matrix

| Paper | Primary object | Information representation | Cleanup | Main resource emphasis |
|---|---|---|---|---|
| Schrottenloher | affine point addition and in-place multiplication | compressed binary-Euclid transcript | reverse transcript construction and measured predicates | low gate count at moderate width |
| Litinski | schoolbook and Montgomery multiplication | signed shifted accumulation plus global corrections | copy and reverse for clean modular product | lower Toffoli count |
| Luongo et al. | modular adders and comparison | retained data plus one measured Boolean outcome | expected self-adjoint phase repair | expected gate count |
| Gidney | classical-quantum addition | streamed carries converted to phase tasks | carry-XOR reconstruction | constant clean workspace |
| Kornerup et al. | dependency graphs | pebbles, ghosts, and classical phase records | recompute and unghost | time–qubit frontier |
| Luo et al. | exact EEA and affine point addition | two shared work registers plus quantum lengths | full-register phase repair | minimum logical width |
| Khattar et al. | polynomial EEA | explicit coefficients or Dialog transitions | reverse transition sequence | input-size-leading space |
| Häner et al. | integrated ECDLP arithmetic | Montgomery values and fixed Kaliski state | caller-aware reverse and workspace reuse | width, T count, and T depth tradeoffs |

## Quick selection

| Question | Start with |
|---|---|
| How can Euclid information be stored? | Schrottenloher, Luo, Khattar |
| How can measurement release workspace? | Luongo, Gidney, Luo, Kornerup |
| How can control overhead be reduced? | Litinski, Luongo, Gidney, Häner |
| How can arithmetic exploit secp256k1? | Schrottenloher |
| How can producer and consumer lifetimes be fused? | Häner |
| How can general recomputation schedules be reasoned about? | Kornerup |
