# Location-controlled arithmetic

## Why it exists

Luo et al. achieve low space by letting multiple logical values share two physical work registers. Their sizes and boundaries vary with the input, so an operation cannot be wired to one fixed slice.

The layout state is:

```text
Work1: t | q | r
Work2: shifted/wrapped t' plus r'
lengths: ell_t, ell_q, ell_r', ell_s
```

A location-controlled operation has two levels of control:

1. the global step `T` determines a classical active interval `[k(T),K(T)]`;
2. a quantum length/index value selects the actual location within that interval.

## Primitive family

**[PAPER]**

```text
selected one-bit swap:
  2(K-k) Toffoli

r-side add/sub:
  11(K-k) Toffoli

t-side add/sub:
   9(K-k) Toffoli

length update:
  24(K-k) Toffoli
  K-k+1 restored dirty bits
```

Unary iteration provides the selector with linear gate cost and logarithmic clean space.

## Architectural tradeoff

The approach replaces:

```text
more fixed-position storage
```

with:

```text
less storage
+ dynamic selection
+ boundary maintenance
+ circular alignment logic
```

That is favorable when qubit minimization is primary. It may be unfavorable for a product objective if selector and ripple costs dominate.

## Transfer to a benchmark implementation

Four layers can be adopted independently:

1. **Lifetime proof** — prove which field slices are inactive at each step.
2. **Allocator reuse** — overlap physical storage without changing arithmetic.
3. **Dirty borrowing** — use inactive slices as restored scratch.
4. **Literal location-controlled arithmetic** — make positions coherent and dynamic.

Start with the first two. They preserve existing low-gate arithmetic and test whether the liveness information alone lowers peak width.

Relevant nodes:

- [`luo-active-windows.md`](../nodes/luo-active-windows.md)
- [`luo-unary-iteration.md`](../nodes/luo-unary-iteration.md)
- [`luo-location-controlled-add-sub.md`](../nodes/luo-location-controlled-add-sub.md)
- [`luo-dirty-length-update.md`](../nodes/luo-dirty-length-update.md)

