---
kind: source-page
source_id: arXiv:2507.23079v1
source_pdf: raw/2507.23079v1.pdf
source_page: 7
---

# A Classical-Quantum Adder with Constant Workspace and Linear Gates - source page 7

The text below is a page-delimited extraction of the unchanged source PDF.

2.4 Borrowing Back and Forth
In [HRS17], a key idea was to split the addition into two halves. I will similarly split the addition
into two halves but, instead of recursively dividing each half into quarters and so forth, I intend
to apply Figure 4 to each half while borrowing the other as dirty qubits. The steps are as follows:
1. Perform a vented addition into the bottom half of the target register (the least significant
half). Crucially, this addition needs to compute the carry qubit needed for the top half
addition. Note that a carry-xorcan’t be merged into the bottom half addition, because it
would need to borrow the top half now but the top half needs to be unperturbed for the next
step.
2. Perform a vented addition into the top half. This addition does include a merged carry-xor,
borrowing the bottom half as the dirty target.
3. Fix phases vented by the top half addition, by targeting the bottom half with a carry-xor
conjugated by classically controlled Z gates. The top half of the register is now finished.
4. Vent the bottom-to-top carry qubit (produce a phasing task by measuring it in the X basis)
now that it’s no longer needed by the top half of the addition.
5. Fix phases vented by the addition into the bottom half. The top half is now available to be
borrowed, and so can be targeted by two carry-xors interleaved with classically controlled Z
gates. This completes the entire addition.
This construction uses 3 clean qubits (two for the vented additions and one to hold the bottom-
to-top carry qubit) and4n±O(1) Toffolis (n±O(1) for the streaming additions and3n±O(1) for
carry-xors). An example circuit is shown in Figure 5.
An interesting property of the adders presented in this paper is that they can all be controlled
at no additional Toffoli cost. To control an addition by an offset ofd, replace every instance of
dk where dk = 0 with 0 and every instance ofdk where dk = 1 with a usage of the control qubit.
Because dk is only ever used to invert controls and to control bit flips, this replacement introduces
no new Toffoli gates. An example is shown in Figure 6. Another nice property all the shown
circuits have is that the carry input qubit is only ever used as a control, meaning it can easily be
replaced by a bit or removed entirely.
To generate other instances of the addition circuits shown in this paper, I refer readers to the
Python code in the Zenodo upload [Gid25].
3 Conclusion
In this paper, I used “venting” (transforming unwanted qubits into unwanted phasing tasks by X ba-
sis measurement) to construct space-efficient quantum-classical adders. I showed that a quantum-
classical addition could be performed using3n±O(1) Toffolis when assisted byn−2 dirty qubits
and 2 clean qubits, or with4n±O(1) Toffolis when assisted by3 clean qubits. I also noted that
these constructions can be controlled at no additional Toffoli cost.
One downside of the constructions in this paper is their linear depth. This is somewhat inherent
to the goal of using constant workspace, since in practice applying operations in parallel requires
workspace proportional to the parallelism to accommodate routing and magic production. I leave
findinglowdepthtradeoffsasfutureworkforotherstoattempt. Itwouldbeparticularlyinteresting
if venting could be used to finally create a true quantum carry-save adder; something able to
accumulate offsets withO(1) marginal depth while usingO(n) storage. Existing attempts at carry-
save adders aren’t "true" because they have anΩ(lg n) or Ω(lg lg 1/ϵ) multiplicative overhead on
the storage or the depth [Gos98; Dra00; Gid19a; Kim+25; Kim25].
I’ll close the paper by noting some personal significance. My first research contribution was a
linear-cost constant-workspace quantum incrementer [Gid15]. I’ve wanted to know how to extend
it to arbitrary offsets for10 years. In fact, based on private conversations, this problem was a
bugbear for many researchers who work on quantum arithmetic circuits (because it appears in
other tasks, like computing superposed multiplicative inverses). In hindsight, the construction
seems so simple. I can’t explain why it took us so long to find it. I’m just glad we finally have it.
7
