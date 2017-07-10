# Infix operators like 5 <<isa>> int

from infix import shift_infix, mod_infix, sub_infix

@shift_infix
def approxeq(a, b):
	"""This takes 1e-09 * max(abs(a), abs(b)), which may not be appropriate."""
	"""Example: 5 <<approxeq>> 5.000000000000001"""
	return abs(a - b) < 1e-09 * max(abs(a), abs(b))

@shift_infix
def isa(x, cls): return x.__class__ == cls


@sub_infix
def o(a, b):
	"""Usage:
	print({'a': 1, 'b': 2, 'c': 3} -o- 'c')
	print({'a': 1, 'b': 2, 'c': 3} -o- {'b', 'c'})
	"""
	return {k: v for k, v in a.items() if k not in b}


@mod_infix
def eq(a, b):
	"""Approximately equal. This takes 1e-09 * max(abs(a), abs(b)), which may not be appropriate."""
	"""Example: 5 %eq% 5.000000000000001"""
	return abs(a - b) < 1e-09 * max(abs(a), abs(b))

@mod_infix
def neq(a, b):
	"""Not approximately equal. This takes 1e-09 * max(abs(a), abs(b)), which may not be appropriate."""
	"""Example: 5 %eq% 5.000000000000001"""
	return abs(a - b) >= 1e-09 * max(abs(a), abs(b))
