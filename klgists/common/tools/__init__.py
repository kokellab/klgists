from klgists.common import *
from typing import Generator, Tuple, Type
from klgists.common.exceptions import RefusingRequestException
from contextlib import contextmanager
from datetime import datetime, date
from collections import defaultdict
from pathlib import Path, PurePath
from hurry.filesize import size as hsize


import numpy as np
import tempfile
import abc

T = TypeVar('T')
Y = TypeVar('Y')
Z = TypeVar('Z')


PLike = Union[str, PurePath, os.PathLike]


class JsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, np.ndarray):
			return obj.tolist()
		elif isinstance(obj, (datetime, date)):
			return obj.isoformat()
		return json.JSONEncoder.default(self, obj)


class Writeable(metaclass=abc.ABCMeta):

	def write(self, msg):
		raise NotImplementedError()

	def flush(self):
		raise NotImplementedError()

	def close(self):
		raise NotImplementedError()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()


class DevNull(Writeable):
	"""Pretends to write but doesn't."""
	def write(self, msg): pass
	def flush(self): pass
	def close(self): pass

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()


class VeryCommonTools:

	@staticmethod
	def to_true_iterable(s: Any) -> Iterable[Any]:
		if VeryCommonTools.is_true_iterable(s):
			return s
		else:
			return [s]

	@staticmethod
	def is_true_iterable(s: Any) -> bool:
		"""
		Returns whether `s` is a probably "proper" iterable -- not a string or bytes
		"""
		return s is not None and isinstance(s, Iterable) and not isinstance(s, str) and not isinstance(s, bytes)

	@staticmethod
	@contextmanager
	def null_context():
		yield

	@staticmethod
	def strip_empty_decimal(num: Union[int, str]) -> str:
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


class CommonTools(VeryCommonTools):

	@staticmethod
	def zip_strict(*args: Iterable[Any]) -> Generator[Tuple[Any], None, None]:
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

	@staticmethod
	def zip_list(*args) -> List[Tuple[Any]]:
		"""
		Same as `zip_strict`, but converts to a list and can provide a more detailed error message.
		:raises: LengthMismatchError
		"""
		try:
			return list(CommonTools.zip_strict(*args))
		except LengthMismatchError:
			raise LengthMismatchError(
				"Length mismatch in zip_strict: Sizes are {}".format([len(x) for x in args])) from None

	@staticmethod
	def forever() -> Iterator[int]:
		"""
		Yields i for i in range(0, infinity).
		Useful for simplifying a i = 0; while True: i += 1 block.
		"""
		i = 0
		while True:
			yield i
			i += 1

	@staticmethod
	def pretty_dict(dct: Mapping[Any, Any]) -> str:
		"""
		Returns a pretty-printed dict, complete with indentation. Will fail on non-JSON-serializable datatypes.
		"""
		return json.dumps(dct, default=JsonEncoder().default, sort_keys=True, indent=4)

	@staticmethod
	def pp_dict(dct: Mapping[Any, Any]) -> None:
		"""Pretty-prints a dict to stdout."""
		print(CommonTools.pretty_dict(dct))

	@staticmethod
	def look(obj: Y, attrs: Union[str, Iterable[str], Callable[[Y], Z]]) -> Optional[Z]:
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
		if attrs is None:
			return obj
		if not isinstance(attrs, str) and hasattr(attrs, '__len__') and len(attrs) == 0:
			return obj
		if isinstance(attrs, str):
			attrs = operator.attrgetter(attrs)
		elif isinstance(attrs, Iterable) and all((isinstance(a, str) for a in attrs)):
			attrs = operator.attrgetter('.'.join(attrs))
		elif not callable(attrs):
			raise TypeError(
				"Type {} unrecognized for key/attribute. Must be a function, a string, or a sequence of strings".format(
					type(attrs)))
		try:
			return attrs(obj)
		except AttributeError:
			return None

	@staticmethod
	def iter_rc(n_rows: int, n_cols: int) -> Generator[Tuple[int, int], None, None]:
		"""
		An iterator over (row column) pairs for a row-first traversal of a grid with `n_cols` columns.
		Ex:
			it = CommonTools.iter_rc(5, 3)
			[next(it) for _ in range(5)]  # [(0,0),(0,1),(0,2),(1,0),(1,1)]
		"""
		for i in range(n_rows * n_cols):
			yield i // n_cols, i % n_cols

	@staticmethod
	def is_lambda(function: Any) -> bool:
		LAMBDA = lambda: 0
		if not hasattr(function, '__name__'): return False  # not a function
		return (
				isinstance(function, type(LAMBDA)) and function.__name__ == LAMBDA.__name__
				or str(function).startswith('<function <lambda> at ') and str(function).endswith('>')
		)

	@staticmethod
	def multidict(
			sequence: Iterable[Z],
			key_attr: Union[str, Iterable[str], Callable[[Y], Z]],
			skip_none: bool = False
	) -> Mapping[Y, Sequence[Z]]:
		"""
		Builds a mapping of some attribute in `sequence` to the containing elements of `sequence`.
		:param sequence: Any iterable
		:param key_attr: Usually string like 'attr1.attr2'; see `look`
		:param skip_none: If None, raises a `KeyError` if the key is missing for any item; otherwise, skips it
		"""
		dct = defaultdict(lambda: [])
		for item in sequence:
			v = CommonTools.look(item, key_attr)
			if not skip_none and v is None:
				raise KeyError("No {} in {}".format(key_attr, item))
			if v is not None:
				dct[v].append(item)
		return dct

	@staticmethod
	def try_none(function: Callable[[], T], fail_val: Optional[T] = None, exception=Exception) -> Optional[T]:
		"""
		Returns the value of a function or None if it raised an exception.
		:param function: Try calling this function
		:param fail_val: Return this value
		:param exception: Restrict caught exceptions to subclasses of this type
		:return:
		"""
		try:
			return function()
		except exception:
			return fail_val

	@staticmethod
	def succeeds(function: Callable[[], Any], exception=Exception) -> bool:
		"""Returns True iff `function` does not raise an error."""
		return CommonTools.try_none(function, exception=exception) is not None

	@staticmethod
	def or_null(x: Any, dtype=lambda s: s, or_else: Any = None) -> Optional[Any]:
		return or_else if CommonTools.is_null(x) else dtype(x)

	@staticmethod
	def or_raise(x: Any, dtype=lambda s: s, or_else: Union[None, BaseException, Type[BaseException]] = None) -> Any:
		"""
		Returns `dtype(x)` if `x` is not None, or raises `or_else`.
		"""
		if or_else is None:
			or_else = LookupError("Value is {}".format(x))
		elif isinstance(or_else, type):
			or_else = or_else("Value is {}".format(x))
		if CommonTools.is_null(x):
			raise or_else
		return dtype(x)

	@staticmethod
	def tmppath(path: Optional[PLike] = None, **kwargs) -> Generator[Path, None, None]:
		if path is None:
			path = tempfile.mktemp()
		try:
			yield Path(path, **kwargs)
		finally:
			Path(path).unlink()

	@staticmethod
	def tmpfile(path: Optional[PLike] = None, spooled: bool = False, **kwargs) -> Generator[Writeable, None, None]:
		if spooled:
			with tempfile.SpooledTemporaryFile(**kwargs) as x:
				yield x
		elif path is None:
			with tempfile.TemporaryFile(**kwargs) as x:
				yield x
		else:
			with tempfile.NamedTemporaryFile(str(path), **kwargs) as x:
				yield x

	@staticmethod
	def tmpdir(**kwargs) -> Generator[Path, None, None]:
		with tempfile.TemporaryDirectory(**kwargs) as x:
			yield Path(x)

	@staticmethod
	def only(sequence: Iterable[Any], condition: Union[str, Callable[[Any], bool]] = None,
			name: str = 'collection') -> Any:
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
			return _only([s for s in sequence if
				(not getattr(s, condition[1:]) if condition.startswith('!') else getattr(s, condition))])
		elif condition:
			return _only([s for s in sequence if condition(s)])
		else:
			return _only(sequence)

	@staticmethod
	def iterator_has_elements(x: Iterator[Any]) -> bool:
		"""
		Returns False `next(x)` raises a `StopIteration`.
		WARNING: Tries to call `next(x)`, progressing iterators. Don't use `x` after calling this.
		Note that calling `iterator_has_elements([5])` will raise a `TypeError`
		:param x: Must be an Iterator
		"""
		return CommonTools.succeeds(lambda: next(x), StopIteration)

	@staticmethod
	def is_null(x: Any) -> bool:
		"""
		Returns True if x is either:
			- None
			- NaN
		"""
		return x is None or isinstance(x, np.float) and np.isnan(x) or (isinstance(x, float) and x == float('nan'))

	@staticmethod
	def is_empty(x: Any) -> bool:
		"""
		Returns True iff either:
			- x is None
			- np.is_nan(x)
			- x is something with 0 length
			- x is iterable and has 0 elements (will call `__iter__`)
		:raises RefusingRequestError If `x` is an Iterator. Calling this would empty the iterator, which is dangerous.
		"""
		if isinstance(x, Iterator):
			raise RefusingRequestException("Do not call is_empty on an iterator.")
		return x is None or isinstance(x, np.float) and np.isnan(x) or (
					isinstance(x, float) and x == float('nan')) or hasattr(x, '__len__') and len(x) == 0 or hasattr(x,
																													'__iter__') and len(
			list(iter(x))) == 0

	@staticmethod
	def is_probable_null(x: Any) -> bool:
		"""
		Returns True iff either:
			- x is None
			- np.is_nan(x)
			- x is something with 0 length
			- x is iterable and has 0 elements (will call `__iter__`)
			- a str(x) is 'nan', 'null', or 'none'; case-insensitive
		In contrast to is_nan, also returns True if x==''.
		:raises TypeError If `x` is an Iterator. Calling this would empty the iterator, which is dangerous.
		"""
		return CommonTools.is_empty(x) or str(x).lower() in ['nan', 'null', 'none']

	@staticmethod
	def unique(sequence: Iterable[T]) -> Sequence[T]:
		"""
		Returns the unqiue items in `sequence`, in the order they appear in the iteration.
		:param sequence: Any once-iterable sequence
		:return: An ordered List of unique elements
		"""
		seen = set()
		return [x for x in sequence if not (x in seen or seen.add(x))]

	@staticmethod
	def first(collection: Iterable[Any], attr: Optional[str] = None) -> Optional[Any]:
		"""
		Returns:
			- The attribute of the first element if `attr` is defined on an element
			- None if the the sequence is empty
			- None if the sequence has no attribute `attr`
		WARNING: Tries to call `next(x)`, progressing iterators.
		:param collection: Any iterable
		:param attr: The name of the attribute that might be defined on the elements, or None to indicate the elements themselves should be used
		:return: The first element, or None
		"""
		try:
			# note: calling iter on an iterator creates a view only
			x = next(iter(collection))
			return x if attr is None else CommonTools.look(x, attr)
		except StopIteration:
			return None

	@staticmethod
	def mem_size(obj) -> str:
		"""
		Returns the size of the object in memory as a human-readable string.
		:param obj: Any Python object
		:return: A human-readable size with units
		"""
		return hsize(sys.getsizeof(obj))

	@staticmethod
	def devnull():
		"""
		Yields a 'writer' that does nothing.
		Ex:
		```
			with Tools.devnull() as devnull:
				devnull.write('hello')
		```
		"""
		yield DevNull()
