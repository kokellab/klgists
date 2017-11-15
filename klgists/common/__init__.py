import os
from itertools import chain
import operator
from typing import Callable, TypeVar, Iterable, Optional, List

def look(obj: object, attrs: str) -> any:
	if not isinstance(attrs, str) and isinstance(attrs, Iterable): attrs = '.'.join(attrs)
	try:
		return operator.attrgetter(attrs)(obj)
	except AttributeError: return None

def flatmap(func, *iterable):
	return chain.from_iterable(map(func, *iterable))

def flatten(*iterable):
	return list(chain.from_iterable(iterable))

class DevNull:
	def write(self, msg): pass

pjoin = os.path.join
pexists = os.path.exists
pdir = os.path.isdir
pfile = os.path.isfile
pis_dir = os.path.isdir
fsize = os.path.getsize
def pardir(path: str, depth: int=1):
	for _ in range(-1, depth):
		path = os.path.dirname(path)
	return path
def grandpardir(path: str):
	return pardir(path, 2)


T = TypeVar('T')
def try_index_of(element: List[T], list_element: T) -> Optional[T]:
	try:
		index_element = list_element.index(element)
		return index_element
	except ValueError:
		return None

T = TypeVar('T')

def exists(keep_predicate: Callable[[T], bool], seq: Iterable[T]) -> bool:
	"""Efficient existential quantifier for a filter() predicate.
	Returns true iff keep_predicate is true for one or more elements."""
	for e in seq:
		if keep_predicate(e): return True  # short-circuit
	return False


def zip_strict(*args):
	"""Same as zip(), but raises a ValueError if the lengths don't match."""
	iters = [iter(axis) for axis in args]
	n_elements = 0
	failures = []
	while len(failures) == 0:
		n_elements += 1
		values = []
		failures = []
		for axis, iterator in enumerate(iters):
			try:
				values.append(next(iterator))
			except StopIteration:
				failures.append(axis)
		if len(failures) == 0:
			yield tuple(values)
	if len(failures) == 1:
		raise ValueError("Too few elements ({}) along axis {}".format(n_elements, failures[0]))
	elif len(failures) < len(iters):
		raise ValueError("Too few elements ({}) along axes {}".format(n_elements, failures))


class Comparable:
	"""A class that's comparable. Just implement __lt__. Credit ot Alex Martelli on https://stackoverflow.com/questions/1061283/lt-instead-of-cmp"""

	def __eq__(self, other):
		return not self < other and not other < self

	def __ne__(self, other):
		return self < other or other < self

	def __gt__(self, other):
		return other < self

	def __ge__(self, other):
		return not self < other

	def __le__(self, other):
		return not other < self
