import random

import numpy as np

'''
diamond square generation
a map of 2^n+1 Width is th assumptino
square map
parameters->  dimensions in
'''

np.set_printoptions(linewidth=200)


def fixed(d, i, j, v, offsets):
	n = d.shape[0]
	
	res, k = 0, 0
	for p, q in offsets:
		pp, qq = i + p * v, j + q * v
		if 0 <= pp < n and 0 <= qq < n:
			res += d[pp, qq]
			k += 1.0
	return res / k


def periodic(d, i, j, v, offsets):
	n = d.shape[0] - 1
	res = 0
	for p, q in offsets:
		res += d[(i + p * v) % n, (j + q * v) % n]
	return res / 4.0


# @jit(nopython=True)
def single_diamond_square_step(d, w, s, avg):
	n = d.shape[0]
	v = w // 2
	
	diamond = np.array([[-1, -1], [-1, 1], [1, 1], [1, -1]])
	square = np.array([[-1, 0], [0, -1], [1, 0], [0, 1]])
	
	for i in range(v, n, w):
		for j in range(v, n, w):
			d[i, j] = avg(d, i, j, v, diamond) + random.uniform(-s, s)
	
	# Square Step, rows
	for i in range(v, n, w):
		for j in range(0, n, w):
			d[i, j] = periodic(d, i, j, v, square) + random.uniform(-s, s)
	
	# Square Step, cols
	for i in range(0, n, w):
		for j in range(v, n, w):
			d[i, j] = periodic(d, i, j, v, square) + random.uniform(-s, s)


#TODO make faster as once 2**10^1 takes ten seconds
#jit might be the best or convert to a pyc to precompile using pyx -> need to include python headers
def diamondSquareGenerator(n: int, ds: float, bdry: staticmethod = periodic) -> np.ndarray:
	d = np.zeros((n, n))
	
	w, s = n - 1, 1.0
	while w > 1:
		single_diamond_square_step(d, w, s, bdry)
		
		w //= 2
		s *= ds
	
	return d
