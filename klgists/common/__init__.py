import os, json, sys
import unicodedata
from itertools import chain
import signal
from datetime import date, datetime
import operator
from datetime import date, datetime
from typing import Callable, TypeVar, Iterable, Optional, List, Any

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
	"""Same as zip(), but raises an IndexError if the lengths don't match."""
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
		raise IndexError("Too few elements ({}) along axis {}".format(n_elements, failures[0]))
	elif len(failures) < len(iters):
		raise IndexError("Too few elements ({}) along axes {}".format(n_elements, failures))


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


def json_serial(obj):
	"""JSON serializer for objects not serializable by default json code.
	From jgbarah at https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable
	"""
	if isinstance(obj, (datetime, date)):
		return obj.isoformat()
	try:
		import peewee
		if isinstance(obj, peewee.Field):
			return type(obj).__name__
	except ImportError: pass
	raise TypeError("Type %s not serializable" % type(obj))

def pretty_dict(dct: dict) -> str:
	"""Returns a pretty-printed dict, complete with indentation. Will fail on non-JSON-serializable datatypes."""
	return json.dumps(dct, default=json_serial, sort_keys=True, indent=4)

def pp_dict(dct: dict) -> None:
	"""Pretty-prints a dict to stdout."""
	print(pretty_dict(dct))

def pp_size(obj: object) -> None:
	"""Prints to stdout a human-readable string of the memory usage of arbitrary Python objects. Ex: 8M for 8 megabytes."""
	print(_hurrysize(sys.getsizeof(obj)))

def sanitize_str(value: str) -> str:
	"""Removes Unicode control (Cc) characters EXCEPT for tabs (\t), newlines (\n only), line separators (U+2028) and paragraph separators (U+2029)."""
	return "".join(ch for ch in value if unicodedata.category(ch) != 'Cc' and ch not in {'\t', '\n', '\u2028', '\u2029'})

def escape_for_properties(value: Any) -> str:
	return sanitize_str(str(value).replace('\n', '\u2028'))

def escape_for_tsv(value: Any) -> str:
	return sanitize_str(str(value).replace('\n', '\u2028').replace('\t', ' '))
	
class Timeout:
	def __init__(self, seconds: int = 10, error_message='Timeout'):
		self.seconds = seconds
		self.error_message = error_message
	def handle_timeout(self, signum, frame):
		raise TimeoutError(self.error_message)
	def __enter__(self):
		signal.signal(signal.SIGALRM, self.handle_timeout)
		signal.alarm(self.seconds)
	def __exit__(self, type, value, traceback):
		signal.alarm(0)

