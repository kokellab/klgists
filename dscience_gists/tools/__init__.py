from typing import Any, Iterable, Union, Callable, Optional, TypeVar, Generator, Tuple, List, Iterator
import sys
from contextlib import contextmanager
import logging
from dscience_gists.core import look as _look
from dscience_gists.core.exceptions import LengthMismatchError, MultipleMatchesException
logger = logging.getLogger('dscience_gists')
Y = TypeVar('Y')
T = TypeVar('T')
Z = TypeVar('Z')


class VeryCommonTools:

	@classmethod
	def is_lambda(cls, function: Any) -> bool:
		LAMBDA = lambda: 0
		if not hasattr(function, '__name__'): return False  # not a function
		return (
				isinstance(function, type(LAMBDA)) and function.__name__ == LAMBDA.__name__
				or str(function).startswith('<function <lambda> at ') and str(function).endswith('>')
		)

	@classmethod
	def only(cls, sequence: Iterable[Any], condition: Union[str, Callable[[Any], bool]] = None, name: str = 'collection') -> Any:
		"""
		Returns either the SINGLE (ONLY) UNIQUE ITEM in the sequence or raises an exception.
		Each item must have __hash__ defined on it.
		:param sequence: A list of any items (untyped)
		:param condition: If nonnull, consider only those matching this condition
		:param name: Just a name for the collection to use in an error message
		:return: The first item the sequence.
		:raises: LookupError If the sequence is empty
		:raises: MultipleMatchesException If there is more than one unique item.
		"""

		def _only(sq):
			st = set(sq)
			if len(st) > 1:
				raise MultipleMatchesException("More then 1 item in " + str(name))
			if len(st) == 0:
				raise LookupError("Empty " + str(name))
			return next(iter(st))

		if condition and isinstance(condition, str):
			return _only([s for s in sequence if (not getattr(s, condition[1:]) if condition.startswith('!') else getattr(s, condition))])
		elif condition:
			return _only([s for s in sequence if condition(s)])
		else:
			return _only(sequence)

	@classmethod
	def zip_strict(cls, *args: Iterable[Any]) -> Generator[Tuple[Any], None, None]:
		"""
		Same as zip(), but raises an IndexError if the lengths don't match.
		:raises: LengthMismatchError
		"""
		# we need to catch these cases before or they'll fail
		# in particular, 1 element would fail with a LengthMismatchError
		# and 0 elements would loop forever
		if len(args) < 2:
			yield from zip(*args)
		iters = [iter(axis) for axis in args]
		n_elements = 0
		failures = []
		while len(failures) == 0:
			values = []
			failures = []
			for axis, iterator in enumerate(iters):
				try:
					values.append(next(iterator))
				except StopIteration:
					failures.append(axis)
			if len(failures) == 0:
				yield tuple(values)
			elif len(failures) == 1:
				raise LengthMismatchError("Too few elements ({}) along axis {}".format(n_elements, failures[0]))
			elif len(failures) < len(iters):
				raise LengthMismatchError("Too few elements ({}) along axes {}".format(n_elements, failures))
			n_elements += 1

	@classmethod
	def zip_list(cls, *args) -> List[Tuple[Any]]:
		"""
		Same as `zip_strict`, but converts to a list and can provide a more detailed error message.
		:raises: LengthMismatchError
		"""
		try:
			return list(cls.zip_strict(*args))
		except LengthMismatchError:
			raise LengthMismatchError(
				"Length mismatch in zip_strict: Sizes are {}".format([len(x) for x in args])) from None

	@classmethod
	def forever(cls) -> Iterator[int]:
		"""
		Yields i for i in range(0, infinity).
		Useful for simplifying a i = 0; while True: i += 1 block.
		"""
		i = 0
		while True:
			yield i
			i += 1

	@classmethod
	def to_true_iterable(cls, s: Any) -> Iterable[Any]:
		if VeryCommonTools.is_true_iterable(s):
			return s
		else:
			return [s]

	@classmethod
	def is_true_iterable(cls, s: Any) -> bool:
		"""
		Returns whether `s` is a probably "proper" iterable -- not a string or bytes
		"""
		return s is not None and isinstance(s, Iterable) and not isinstance(s, str) and not isinstance(s, bytes)

	@classmethod
	@contextmanager
	def null_context(cls):
		yield

	@classmethod
	def strip_empty_decimal(cls, num: Union[int, str]) -> str:
		"""
		Replaces prefix . with 0. and strips trailing .0 and trailing .
		"""
		t = str(num)
		if t.startswith('.'):
			t = '0' + t
		if '.' in t:
			return t.rstrip('0').rstrip('.')
		else:
			return t

	@classmethod
	def look(cls, obj: Y, attrs: Union[str, Iterable[str], Callable[[Y], Z]]) -> Optional[Z]:
		"""
		Returns the value of a chain of attributes on object `obj`, or None any object in that chain is None or lacks the next attribute.
		For example::
			CommonTools.look(kitten), 'breed.name')  # either None or a string
		:param obj: Any object
		:param attrs: One of:
				- A string in the form attr1.attr2, translating to `obj.attr1`
				- An iterable of strings of the attributes
				- A function that maps `obj` to its output; equivalent to calling `attrs(obj)` but returning None on `AttributeError`.
		:return: Either None or the type of the attribute
		:raises: TypeError
		"""
		return _look(obj, attrs)

	@classmethod
	def get_log_function(cls, log: Union[None, str, Callable[[str], None]]) -> Callable[[str], None]:
		"""
		Gets a logging function from user input.
		The rules are:
			- If None, uses logger.info
			- If 'print' or 'stdout',  use sys.stdout.write
			- If 'stderr', use sys.stderr.write
			- If another str or int, try using that logger level (raises an error if invalid)
			- If callable, returns it
			- If it has a callable method called 'write', uses that
		:return: A function of the log message that returns None
		"""
		if log is None:
			return logger.info
		elif log in ['print', 'stdout']:
			return lambda msg: sys.stdout.write(msg)
		elif log == 'stderr':
			return lambda msg: sys.stderr.write(msg)
		elif isinstance(log, int):
			return getattr(logger, logging.getLevelName(log))
		elif isinstance(log, str):
			return getattr(logger, logging.getLevelName(log.upper()))
		elif callable(log):
			return log
		elif hasattr(log, 'write') and getattr(log, 'write'):
			return getattr(log, 'write')
		else:
			raise TypeError("Log type {} not known".format(type(log)))

	def __repr__(self): return self.__class__.__name__
	def __str__(self): return self.__class__.__name__


__all__ = ['VeryCommonTools']
