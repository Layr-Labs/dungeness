# Controlled and constant arithmetic

The papers expose several distinct ways to reduce control overhead.

## Gidney

A classical offset is incorporated directly into the carry process. An outer
control can replace offset literals equal to one without adding Toffolis in the
paper's accounting.

## Litinski

Control selects addition or subtraction instead of addition or identity.
Global algebraic corrections remove the unwanted signed branches.

## Luongo

Only boundary operations whose semantics depend on the external control need
that control. The final Boolean cleanup can be measured and repaired in
expectation.

## Schrottenloher

For `p=2^256-2^32-977`, selected full-modulus corrections become additions of
the short constant `2^32+977`.

## Häner

Classical constants may be loaded into a register or curried into the gate
sequence; the surrounding arithmetic determines which width–gate tradeoff is
appropriate.
