---
kind: source-page
source_id: arXiv:2110.08973v3
source_pdf: raw/2110.08973v3.pdf
source_page: 22
---

# Tight Bounds on the Spooky Pebble Game: Recycling Qubits with Measurements - source page 22

The text below is a page-delimited extraction of the unchanged source PDF.

Unrolling the recurrence gives us thatT(h) is O(h2h), which in turn isO(nlog n). We then note
that U can be converted into a pebbling algorithmP by removing step 6. Doing this does not
change the number of pebbles used and reduces the total number of steps by one, soP also uses
at mosth+ 1 pebbles and onlyO(nlog n) steps.
6 Future work
As the main result of this paper, we have shown asymptotically tight upper and lower bounds for
the spooky pebble game when played on the line graph. Going beyond the line graph presents
significant challenges as the number of pebbles needed in the spooky pebble game to pebble
an arbitrary DAG is PSPACE-hard to approximate. Despite this, for the binary tree graph
with heighth and n= 2h −1 nodes we were able to construct a time-efficient (i.e.O(nlog n))
pebblingstrategythatusestheoptimalnumberofpebbles(i.e. h+1). Thetimeoptimalityofthis
algorithm is unknown and it would be interesting to construct a more time-efficient algorithm for
the binary tree or prove it is impossible. On the other extreme there is a straightforward spooky
pebbling algorithm that usesnpebbles and onlyO(n) steps. Is there a general tradeoff between
the number of pebbles and the number of steps for the binary tree similar to our results for the
line graph? Beyond binary trees we think it would be interesting to explore strategies for the
spooky pebble game on other graph topologies like butterfly graphs used in computing the DFT
[3], and those used in the construction of data-independent memory-hard functions [38, 7, 39].
Finally, the spooky pebble game is but one way to use intermediate measurements to improve
the time-space efficiency of quantum algorithms. Whether other methods of using intermediate
measurements could yield better time and space efficiency tradeoffs remains open.
7 Acknowledgments
We would like to thank Craig Gidney for insightful discourse regarding his blog post on the
spooky pebble game as well as Eddie Schoute and Patrick Rall for discussions about potential
applications of the spooky pebble game. Additionally we would like to thank the anonymous
reviewers of our paper for taking the time to review our manuscript. We sincerely appreciate
their comments and suggestions, which improved the quality of this manuscript.
References
[1] Ravi Sethi. “Complete register allocation problems”. In Proceedings of the Fifth Annual
ACM Symposium on Theory of Computing (STOC 1973). Page 182–195. Association for
Computing Machinery (1973).
[2] John Hopcroft, Wolfgang Paul, and Leslie Valiant. “On time versus space”. J. ACM24,
332–337 (1977).
[3] MartinTompa. “Time-spacetradeoffsforcomputingfunctions, usingconnectivityproperties
of their circuits”. Journal of Computer and System Sciences20, 118–132 (1980).
[4] Wolfgang J. Paul, Robert Endre Tarjan, and James R. Celoni. “Space bounds for a game on
graphs”. In Proceedings of the Eighth Annual ACM Symposium on Theory of Computing
(STOC 1976). Page 149–160. Association for Computing Machinery (1976).
[5] Thomas Lengauer and Robert E. Tarjan. “Asymptotically tight bounds on time-space trade-
offs in a pebble game”. J. ACM29, 1087–1130 (1982).
22
