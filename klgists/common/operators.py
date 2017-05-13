# Infix operators like 5 <<isa>> int

from infix import shift_infix

@shift_infix
def approxeq(a, b):
	"""This takes 1e-09 * max(abs(a), abs(b)), which may not be appropriate."""
	"""Example: 5 <<approxeq>> 5.000000000000001"""
	return abs(a - b) < 1e-09 * max(abs(a), abs(b))

@shift_infix
def isa(x, cls): return x.__class__ == cls
