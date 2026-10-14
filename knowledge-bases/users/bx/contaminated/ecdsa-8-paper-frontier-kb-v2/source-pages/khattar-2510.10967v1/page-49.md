---
kind: source-page
source_id: arXiv:2510.10967v1
source_pdf: raw/2510.10967v1.pdf
source_page: 49
---

# Verifiable Quantum Advantage via Optimized DQI Circuits - source page 49

The text below is a page-delimited extraction of the unchanged source PDF.

49
import numpy as np
from galois import Poly
def poly_eea_zalka_gcd_impl (A: Poly , B: Poly , stop , n_steps : float = 5.0) -> tuple [np. ndarray , int , int ]:
gf , m = A. field , B. degree + 3
a_array , b_array = gf. Zeros (m), gf. Zeros (m)
a_array [0] , a_array [m - A. degree - 1 :] , b_array [m - B. degree - 1 :] = 1, A. coeffs [:: -1] , B. coeffs [:: -1]
n_A , n_B , n_a , n_b , n_q = A. degree + 1, B. degree + 1, 1, 0, 0
flag , counter , halting_counter = 1, 0, 0
def swap_a_and_b ():
nonlocal n_A , n_B , flag , n_a , n_b , a_array , b_array , halting_counter , counter
if counter == 3 and flag and halting_counter == 0:
n_A , n_B = n_B , n_A
n_a , n_b = n_b , n_a
a_array , b_array = b_array , a_array
def update_flag ():
nonlocal flag
if counter == 0 and halting_counter == 0:
flag ^= ( n_q == 0) and ( n_A < n_B )
flag ^= n_A == n_B
elif counter == 1 and halting_counter == 0:
flag ^= n_A == n_B
flag ^= n_B == 1 or b_array [ -2] != 0
elif counter == 2 and halting_counter == 0:
flag ^= b_array [0] != 0 or n_b == 0
flag ^= n_a == n_b + 1
elif counter == 3 and halting_counter == 0:
flag ^= n_a == n_b
flag ^= n_q == 1
else :
assert False
def multiply_and_add_or_sub ():
nonlocal b_array
q_i = 0
if counter == 0 and halting_counter == 0:
q_i ^= ( a_array [ -1] ** -1) * b_array [ -1]
for i in range (m - 1, -1, -1):
swap_if = i == n_a + n_q and counter == 0 and halting_counter == 0
swap_if |= (i + 1) == n_a + n_q and counter == 3 and halting_counter == 0
if swap_if :
q_i , a_array [i] = a_array [i], q_i
q_i_times_a_i = q_i * a_array [i]
add_if = ( counter == 3) and i < n_a
sub_if = ( counter == 0) and i >= m - n_A
if add_if :
b_array [i] += q_i_times_a_i
if sub_if :
b_array [i] -= q_i_times_a_i
if counter == 3 and halting_counter == 0:
q_i ^= b_array [0] * ( a_array [0] ** -1)
assert q_i == 0
def shift_b_array_right ():
nonlocal b_array
for i in range (m - 1, -1, -1):
do_shift = False
if counter == 0:
do_shift = (i >= m - n_B + 1) and not flag
if counter == 1:
do_shift = i >= m - n_B + 1
if counter == 2:
do_shift = 0 < i <= n_b
if counter == 3:
do_shift = (0 < i < m - n_B ) and not flag
if do_shift and halting_counter == 0:
b_array [i - 1] , b_array [i] = b_array [i], b_array [i - 1]
def update_metadata ():
nonlocal n_A , n_B , n_q , flag , n_a , n_b
if counter == 0 and halting_counter == 0:
n_q += 1
if not flag :
n_B -= 1
if counter == 1 and halting_counter == 0:
n_B -= 1
if counter == 2 and halting_counter == 0:
n_b += 1
if counter == 3 and halting_counter == 0:
if not flag :
n_b += 1
n_q -= 1
def check_stop ():
nonlocal halting_counter
if counter == 3 and flag and stop (n_A , n_B , n_a , n_b ):
halting_counter += 1
for it in range ( int (np. ceil ( n_steps * m ))):
update_flag ()
multiply_and_add_or_sub ()
shift_b_array_right ()
update_metadata ()
swap_a_and_b ()
check_stop ()
# Advance counter .
counter = ( counter + flag ) % 4
return b_array , n_b , n_B
FIG. 9: Our optimized implementation of Zalka’s EEA for explicit access to Bézout coefficients.
