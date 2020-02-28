from typing import Iterable, Any, Tuple, Generator, Iterator, Mapping, Union, Callable, Optional, Sequence, TypeVar, Type
import sys
from hurry.filesize import size as hsize
from collections import defaultdict
import numpy as np
from dscience_gists.tools.base_tools import BaseTools
from dscience_gists.core import DevNull
from dscience_gists.core.exceptions import RefusingRequestError
Y = TypeVar('Y')
T = TypeVar('T')
Z = TypeVar('Z')


class CommonTools(BaseTools):

	@classmethod
	def try_none(cls, function: Callable[[], T], fail_val: Optional[T] = None, exception=Exception) -> Optional[T]:
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

	@classmethod
	def succeeds(cls, function: Callable[[], Any], exception=Exception) -> bool:
		"""Returns True iff `function` does not raise an error."""
		return cls.try_none(function, exception=exception) is not None

	@classmethod
	def or_null(cls, x: Any, dtype=lambda s: s, or_else: Any = None) -> Optional[Any]:
		"""
		Return `None` if the operation `dtype` on `x` failed; returns the result otherwise.
		"""
		return or_else if cls.is_null(x) else dtype(x)

	@classmethod
	def or_raise(cls, x: Any, dtype=lambda s: s, or_else: Union[None, BaseException, Type[BaseException]] = None) -> Any:
		"""
		Returns `dtype(x)` if `x` is not None, or raises `or_else`.
		"""
		if or_else is None:
			or_else = LookupError("Value is {}".format(x))
		elif isinstance(or_else, type):
			or_else = or_else("Value is {}".format(x))
		if cls.is_null(x):
			raise or_else
		return dtype(x)

	@classmethod
	def iterator_has_elements(cls, x: Iterator[Any]) -> bool:
		"""
		Returns False `next(x)` raises a `StopIteration`.
		WARNING: Tries to call `next(x)`, progressing iterators. Don't use `x` after calling this.
		Note that calling `iterator_has_elements([5])` will raise a `TypeError`
		:param x: Must be an Iterator
		"""
		return cls.succeeds(lambda: next(x), StopIteration)

	@classmethod
	def is_null(cls, x: Any) -> bool:
		"""
		Returns True if x is either:
			- None
			- NaN
		"""
		return x is None or isinstance(x, np.float) and np.isnan(x) or (isinstance(x, float) and x == float('nan'))

	@classmethod
	def is_empty(cls, x: Any) -> bool:
		"""
		Returns True iff either:
			- x is None
			- np.is_nan(x)
			- x is something with 0 length
			- x is iterable and has 0 elements (will call `__iter__`)
		:raises RefusingRequestError If `x` is an Iterator. Calling this would empty the iterator, which is dangerous.
		"""
		if isinstance(x, Iterator):
			raise RefusingRequestError("Do not call is_empty on an iterator.")
		return (
				x is None
				or isinstance(x, np.float) and np.isnan(x)
				or (isinstance(x, float) and x == float('nan'))
				or hasattr(x, '__len__') and len(x) == 0
				or hasattr(x, 	'__iter__') and len(list(iter(x))) == 0
		)

	@classmethod
	def is_probable_null(cls, x: Any) -> bool:
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
		return cls.is_empty(x) or str(x).lower() in ['nan', 'null', 'none']

	@classmethod
	def unique(cls, sequence: Iterable[T]) -> Sequence[T]:
		"""
		Returns the unique items in `sequence`, in the order they appear in the iteration.
		:param sequence: Any once-iterable sequence
		:return: An ordered List of unique elements
		"""
		seen = set()
		return [x for x in sequence if not (x in seen or seen.add(x))]

	@classmethod
	def first(cls, collection: Iterable[Any], attr: Optional[str] = None) -> Optional[Any]:
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
			return x if attr is None else cls.look(x, attr)
		except StopIteration:
			return None

	@classmethod
	def iter_rc(cls, n_rows: int, n_cols: int) -> Generator[Tuple[int, int], None, None]:
		"""
		An iterator over (row column) pairs for a row-first traversal of a grid with `n_cols` columns.
		Ex:
			it = CommonTools.iter_rc(5, 3)
			[next(it) for _ in range(5)]  # [(0,0),(0,1),(0,2),(1,0),(1,1)]
		"""
		for i in range(n_rows * n_cols):
			yield i // n_cols, i % n_cols

	@classmethod
	def multidict(
			cls,
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

	@classmethod
	def mem_size(cls, obj) -> str:
		"""
		Returns the size of the object in memory as a human-readable string.
		:param obj: Any Python object
		:return: A human-readable size with units
		"""
		return hsize(sys.getsizeof(obj))

	@classmethod
	def devnull(cls):
		"""
		Yields a 'writer' that does nothing.
		Ex:
		```
			with Tools.devnull() as devnull:
				devnull.write('hello')
		```
		"""
		yield DevNull()


__all__ = ['CommonTools']
