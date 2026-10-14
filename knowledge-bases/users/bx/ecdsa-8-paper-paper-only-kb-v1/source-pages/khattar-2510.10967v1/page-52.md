---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 52
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 52

The text below is a page-delimited extraction of the unchanged source PDF.

52
import numpy as np
def construct_dialog (s: np. ndarray , n_iters : int ) -> tuple [np. ndarray , list , int ]:
gf , n = type (s [0]) , len (s)
poly = [gf (0) for _ in range (2 * n + 3)]
poly [0] , poly [-n:] = gf (1) , s
delta = 0
dialog = []
for _ in range ( n_iters ):
# 1. Compute the dialog
is_swap = delta >= 0 and poly [ -1] != 0
if is_swap :
delta , poly = ~ delta , poly [:: -1]
delta = 1 + delta
coeff = poly [ -1] // poly [0]
dialog . append (( coeff , is_swap ))
# 2. Perform omega_x -= coeff * u_x in shared register representation .
for j in range ( len ( poly ) // 2 - 1, -1, -1):
if j < len ( poly ) // 2 + delta // 2:
poly [-j - 1] -= poly [j] * coeff
assert poly . pop () == 0
assert len ( poly ) == 2 * n + 3 - n_iters
return poly , dialog , delta
def rs_syndrome_decoder_eea_dialog_inplace (s: np. ndarray ) -> np. ndarray :
gf , n = type (s [0]) , len (s)
# Compute the dialog representation using Bernstein - Yang style GCD iterations .
# Shared register stores (u_x , omega_x ) such that :
# u_x_ {0} , u_x_ {1} , ... , u_x_ {n}, 0, 0, omega_ {n - 1} , omega_ {n - 2} , ... , omega_0
poly , dialog , delta = construct_dialog (s, n - 1)
def omega_eval (c):
# Evaluate omega using shared register representation . n_omega = n //2 - delta // 2
res = gf (0)
cpow = 1
for j in range (n // 2):
if j < n // 2 - delta // 2:
res += poly [-j - 1] * cpow
cpow = cpow * c
return res
def sigma_and_sigma_prime_eval (c):
# Use the dialog representation to evaluate sigma and sigma_prime directly .
eval_w_x , eval_sigma_x = gf (0) , gf (1)
eval_w_x_prime , eval_sigma_x_prime = gf (0) , gf (0)
for coeff , is_swap in dialog :
if is_swap :
eval_w_x , eval_sigma_x = eval_sigma_x , eval_w_x
eval_w_x_prime , eval_sigma_x_prime = eval_sigma_x_prime , eval_w_x_prime
eval_w_x_prime_times_coeff = eval_w_x_prime * coeff
eval_sigma_x_prime -= eval_w_x_prime_times_coeff
eval_sigma_x_prime = eval_sigma_x_prime * c
eval_sigma_x_prime += eval_sigma_x
eval_w_x_times_coeff = eval_w_x * coeff
eval_sigma_x_prime -= eval_w_x_times_coeff
eval_sigma_x -= eval_w_x_times_coeff
eval_sigma_x = eval_sigma_x * c
ct = n // 2 + delta // 2
eval_sigma_x = eval_sigma_x // c
eval_sigma_x_prime -= ct * eval_sigma_x
return eval_sigma_x , eval_sigma_x_prime
block_length = gf. order - 1
gammas = gf ([ gf. primitive_element **i for i in range ( block_length )])
errors = gf. Zeros ( block_length )
for i in range ( block_length ):
sigma_x_eval , sigma_x_prime_eval = sigma_and_sigma_prime_eval ( gammas [i])
if sigma_x_eval == 0:
j = block_length - i if i else i
const_to_mul = gammas [j] * ( gammas [i] ** n)
errors [j] = const_to_mul * omega_eval ( gammas [j]) * sigma_x_prime_eval ** -1
return errors
FIG. 12: Optimized implementation of EEA based syndrome decoder for RS codes using register sharing to
efficiently compute the Dialog representation and use it to implicitly evaluate Bézout coefficient corresponding to
polynomial σ(z) and σ′(z).
