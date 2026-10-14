---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 48
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 48

The text below is a page-delimited extraction of the unchanged source PDF.

48
Appendix F: Reference Python Implementation
1. Reed Solomon Decoding using Synchronized EEA for Explicit Bézout coefficients
Fig. 9 gives our optimized implementation of Zalka’s synchronized reversible EEA [12]. Fig. 10 uses this as a
subroutine and shows how to implement the Chien Search [23] and Forney’s algorithm [24] steps for syndrome decoding
of Reed Solomon codes, given the shared in-place register representation of the error locator polynomialσ(z) and
error evaluator polynomialΩ(z).
2. Reed Solomon Decoding using Dialog based EEA for Implicit Bézout Coefficients
Fig. 11 gives our optimized implementation of constructing a Dialog based on the Bernstein-Yang GCD algorithm
[17] using a shared register representation to save space. We also show how once can consume the Dialog to perform
modular multiplication or modular division. Fig. 12 uses uses the Dialog based EEA for syndrome decoding of Reed
Solomon codes, and shows how one can evaluate the error locator polynomialσ(z) and it’s derivativeσ′(z), given
access to the Dialog ofσ(z).
