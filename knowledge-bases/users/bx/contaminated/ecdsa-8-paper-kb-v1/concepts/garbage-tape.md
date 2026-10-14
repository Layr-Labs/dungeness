# Euclid history tape and register sharing

## Reachable symbol alphabet

Each Euclid iteration records:

```text
(b0, b0_and_b1)
```

Only three pairs are reachable:

```text
(0,0), (1,0), (1,1)
```

Three iterations therefore have `3^3 = 27` valid blocks, which fit in five bits.

## Paper compressor

**[PAPER]** An ad hoc reversible circuit maps each valid 6-bit block to a 5-bit block and clears one wire. It costs five Toffolis.

**[CODE]** The companion source contains:

- an explicit 27-entry valid-state permutation;
- a 5-Toffoli `Compressor`;
- `Swapper` for exchanging one uncompressed pair with a slot in a compressed block;
- `Absorber` for inserting a pair into an empty slot.

The compressor is not ordinary binary or ternary arithmetic coding. It is a reversible partial-domain permutation synthesized for the 27 reachable states.

## Tape size

For a fixed iteration count `L` rounded to a multiple of three:

```text
tape_bits = 5 * L/3
```

At `n=256`, `L=402`:

```text
tape_bits = 670
```

The information-theoretic lower bound for independent ternary symbols would be:

```text
L * log2(3) ~= 637.1 bits
```

The selected codec pays about 33 bits to keep each 3-step block local and cheap.

## Register sharing

The expected combined reduction per Euclid step lets `u` and `v` shrink. The paper models each current width as approximately:

```text
width(i) = n - 0.5*log2(8/3)*i + c_pad*sqrt(n)
```

where:

```text
0.5*log2(8/3) ~= 0.7075
```

Freed high wires are reused for tape blocks. The companion implementation interleaves the physical `u` and `v` storage, reverses it, takes the tape prefix, and leaves the remainder as padding.

## Why the tape must be fixed-size

A variable-length 1-or-2-bit record per step looks asymptotically smaller, but reversible enqueue/dequeue shifts are expensive and the total length itself fluctuates by `O(sqrt(n))`. The fixed 5-bit block:

- makes allocation static;
- allows direct random access by block;
- avoids a large controlled shift network;
- simplifies reverse traversal;
- makes failure come from known iteration/padding bounds rather than tape overflow.

## Benchmark opportunities

**[INFERENCE]** In a mature benchmark implementation, the highest-value tape work is unlikely to be replacing the 5-bit codec in isolation. A codec saving `dQ` qubits is useful only if:

- those qubits are live at the actual global peak;
- encoder/decoder Toffolis do not exceed the product exchange rate;
- the codec supports reverse streaming without regenerating another large state;
- all 27 reachable blocks and inverse paths are exact.

Potential improvements:

1. fuse decompression with the controlled swap/add logic;
2. use a larger block only if the amortized encoder is cheap;
3. exploit correlations across iterations, not just independent ternary entropy;
4. store a jump-step symbol with a smaller reachable alphabet;
5. overlap tape wires with known-zero coefficient wires during replay.

These are research hypotheses, not consequences of the paper.

## Tests

At minimum:

- exhaustive test of all 27 valid 3-symbol blocks;
- forward/inverse test of the gate sequence on all 64 six-bit inputs if the permutation is totalized;
- random full-history round trips;
- tests with empty tail iterations;
- peak-width measurement proving that released wires reduce the scorer's width.
