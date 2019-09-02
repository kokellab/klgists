"""
Operators used for convenience. Although they increase readability, their use can't be refeactored out automatically.
Carefully decide whether you want to use these.
"""
from typing import Any, Optional
from infix import shift_infix, mod_infix, or_infix


@or_infix
def oelse(opt: Optional[Any], fallback: Any) -> Any:
	"""
	I'm tired of writing `x if x is None else 5`.
	Now it's just `x |o| 5`
	"""
	return fallback if opt is None else opt

@or_infix
def otry(x, func) -> Any:
	"""
	I'm tired of wrapping in try and returning None
	Now it's just `x |otry| func`
	Only catches Exception and its subclasses (ex stack overflows will bubble up).
	"""
	try:
		return func(x)
	except Exception:
		return None

@or_infix
def omap(x, func) -> Any:
	"""
	I'm tired of writing `try_this(x) if x is None else 5`.
	Now it's just `x |omap| func`
	"""
	return None if x is None else func(x)

@or_infix
def oadd(x, y) -> Any:
	"""
	Add two numbers or return None if either is None.
	"""
	return None if x is None or y is None else x + y

@or_infix
def osub(x, y) -> Any:
	"""
	Subtract two numbers or return None if either is None.
	"""
	return None if x is None or y is None else x - y

@or_infix
def omult(x, y) -> Any:
	"""
	Multiply two numbers or return None if either is None.
	"""
	return None if x is None or y is None else x * y

@or_infix
def odiv(x, y) -> Any:
	"""
	Divide two numbers or return None if either is None.
	"""
	return None if x is None or y is None else x / y

@or_infix
def omod(x, y) -> Any:
	"""
	Modulo two numbers or return None if either is None.
	"""
	return None if x is None or y is None else x % y

@shift_infix
def isa(x, cls):
	"""
	Example: 5 %isa% int
	"""
	return isinstance(x, cls)

@mod_infix
def eq(a, b):
	"""
	Approximately equal. This takes 1e-09 * max(abs(a), abs(b)), which may not be appropriate.
	Example: 5 %eq% 5.000000000000001"
	"""
	return abs(a - b) < 1e-09 * max(abs(a), abs(b))

@mod_infix
def neq(a, b):
	"""
	Not approximately equal. This takes 1e-09 * max(abs(a), abs(b)), which may not be appropriate.
	Example: 5 %neq% 5.000000000000001"
	"""
	return abs(a - b) >= 1e-09 * max(abs(a), abs(b))

