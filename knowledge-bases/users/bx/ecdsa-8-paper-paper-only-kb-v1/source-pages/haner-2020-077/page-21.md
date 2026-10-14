---
kind: source-page
source_id: IACR ePrint 2020/077
source_pdf: raw/2020-077.pdf
source_page: 21
---

# Improved quantum circuits for elliptic curve discrete logarithms - source page 21

The text below is a page-delimited extraction of the unchanged source PDF.

Circuit Metric Depth Gates Qubits
In/out Auxiliary Total
Modular Squaring
Low W T 3.54n2 lg n+ 1.32 ·215 5.62n2 lg n+ 1.24 ·216
2n 3n+ 15.1 5n+ 15.1All 11.5n2 lg n+ 1.09 ·217 17.3n2 lg n+ 1.94 ·217
Low T T 21.4n2 + 1.43 ·210 37.8n2 + 1.37 ·212
2n 4n+ 12.3 6n+ 12.3All 75.7n2 + 1.46 ·213 143n2 + 1.74 ·215
Low D T 11.5nlg n+ 1.88 ·29 124n2 + 1.29 ·212
2n 6n+ 11.6 8n+ 11.6All 86.4nlg n+ 1.40 ·211 509n2 + 1.56 ·215
Modular Multiplication
Low W T 3.54n2 lg n+ 1.35 ·215 5.62n2 lg n+ 1.28 ·216
3n 3n+ 15.0 6n+ 15.0All 11.5n2 lg n+ 1.12 ·217 17.3n2 lg n+ 2.00 ·217
Low T T 21.4n2 + 1.35 ·210 37.8n2 + 1.40 ·212
3n 4n+ 12.2 7n+ 12.2All 75.7n2 + 1.45 ·213 143n2 + 1.73 ·215
Low D T 11.4nlg n+ 1.84 ·29 124n2 + 1.29 ·212
3n 6n+ 11.6 9n+ 11.6All 84.8nlg n+ 1.42 ·211 509n2 + 1.54 ·215
Modular Inversion
Low W T 72n2 lg n+ 1.76 ·216 236n2 lg n+ 1.30 ·218
2n 5n+ 1⌊lg n⌋+ 11 7n+ 1⌊lg n⌋+ 11All 233n2 lg n+ 1.44 ·218 703n2 lg n+ 1.49 ·219
Low T T 162n2 + 1.09 ·212 496n2 + 1.70 ·214
2n 7n+ 1⌊lg n⌋+ 11 9n+ 1⌊lg n⌋+ 11All 592n2 + 1.42 ·214 1789n2 + 1.96 ·216
Low D T 84.4nlg n+ 1.10 ·212 1062n2 −1.28 ·216
2n 8n+ 12.8 10n+ 12.8All 529nlg n+ 1.83 ·213 4162n2 −1.28 ·218
Modular Division
Low W T 76n2 lg n+ 1.26 ·217 243n2 lg n+ 1.66 ·218
3n 5n+ 3.1 ⌊lg n⌋+ 9.7 8n+ 3.1 ⌊lg n⌋+ 9.7All 245n2 lg n+ 1.02 ·219 722n2 lg n+ 1.03 ·220
Low T T 184n2 + 1.46 ·212 534n2 + 1.03 ·215
2n 8n+ 1⌊lg n⌋+ 11 10n+ 1⌊lg n⌋+ 11All 667n2 + 1.12 ·215 1932n2 + 1.43 ·217
Low D T 95.8nlg n+ 1.35 ·212 1186n2 −1.13 ·216
2n 9n+ 18.8 11n+ 18.8All 614nlg n+ 1.12 ·214 4672n2 −1.01 ·218
Signed Windowed Elliptic Curve Point Addition (window size 8)
Low W T 144n2 lg n+ 1.19 ·219 503n2 lg n+ 1.26 ·220
2n 6n+ 3.8 ⌊lg n⌋+ 17.1 8n+ 3.8 ⌊lg n⌋+ 17.1All 465n2 lg n+ 1.98 ·220 1423n2 lg n+ 1.99 ·221
Low T T 432n2 + 1.07 ·214 1182n2 + 1.41 ·216
2n 8n+ 1.5 ⌊lg n⌋+ 18.9 10n+ 1.5 ⌊lg n⌋+ 18.9All 1562n2 + 1.85 ·216 4306n2 + 1.31 ·219
Low D T 226nlg n+ 1.77 ·213 2746n2 −1.31 ·216
2n 9n+ 28.6 11n+ 28.6All 1485nlg n+ 1.60 ·215 10891n2 −1.39 ·216
Shor’s algorithm (with signed windowed point addition)
Low W T 120n3 −1.67 ·222 436n3 −1.05 ·226
2n 6n+ 10.2 ⌊lg n⌋−1.0 8n+ 10.2 ⌊lg n⌋−1.0All 509n3 −1.84 ·227 2800n3 −1.08 ·231
Low T T 389n3/lg n−1.70 ·222 1115n3/lg n−1.08 ·224
2n 8n+ 7.4 ⌊lg n⌋+ 1.3 10n+ 7.4 ⌊lg n⌋+ 1.3All 1701n3/lg n−1.23 ·224 6262n3/lg n−1.72 ·224
Low D T 285n2 −1.54 ·217 3120n3/lg n−1.49 ·227
2n 9n+ 3.9 ⌊lg n⌋+ 16.5 11n+ 3.9 ⌊lg n⌋+ 16.5All 2523n2 + 1.10 ·220 12478n3/lg n−1.25 ·229
Table 4: Estimates for non-linear modular arithmetic, elliptic curve point addition and Shor’s
algorithm.
21
