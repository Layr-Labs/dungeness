---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 50
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 50

The text below is a page-delimited extraction of the unchanged source PDF.

50
import numpy as np
from galois import Poly
from poly_eea_zalka_gcd import poly_eea_zalka_gcd_impl
def rs_syndrome_decoder_eea_zalka (s: np. ndarray ) -> np. ndarray :
gf , n = type (s [0]) , len (s)
def _stop_rs ( n_A : int , n_B : int , _: int , __: int ):
return n_A == 0 or n_B < n // 2
A = Poly (s [:: -1] , field =gf)
B = Poly . Degrees ( coeffs =[1] , degrees =[n], field =gf)
b_array , n_b , n_B = poly_eea_zalka_gcd_impl (A, B, stop = _stop_rs , n_steps =3.75)
assert n_B <= n // 2 and n_b <= n // 2
def poly_eval (c):
omega_x_val , sigma_x_val , sigma_x_prime_val = gf (0) , gf (0) , gf (0)
m = len ( b_array )
for i in range (m - 1, m // 2, -1):
c_i = c ** (i)
omega_x_val += b_array [i] * c_i
for i in range (m // 2, -1, -1):
c_i = c ** (-i)
sigma_x_val += b_array [i] * c_i
if i & 1:
sigma_x_prime_val += b_array [i] * c_i
return omega_x_val , sigma_x_val , sigma_x_prime_val
block_length = gf. order - 1
gammas = gf ([ gf. primitive_element **i for i in range ( block_length )])
errors = gf. Zeros ( block_length )
for i in range ( block_length ):
omega_x_eval , sigma_x_eval , sigma_x_prime_eval = poly_eval ( gammas [i])
if sigma_x_eval == 0:
j = block_length - i if i else i
c = gammas [i]
const_to_mul = c ** -( len ( b_array ) - 1 + n_b - n_B - 1)
errors [j] = const_to_mul * omega_x_eval / sigma_x_prime_eval
return errors
FIG. 10: RS Decoding using our optimized implementation of Zalka’s EEA [12, 16] presented in Fig. 9
