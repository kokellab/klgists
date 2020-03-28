from __future__ import annotations
import enum
import logging
from typing import Sequence, Iterable, TypeVar, Any, Callable, Generic, Type
import json
from datetime import date, datetime
import abc
import numpy as np
from dscience.core.exceptions import ImmutableError
# noinspection PyProtectedMember
from dscience.core.internal import PathLike, look as _look
T = TypeVar('T', covariant=True)
logger = logging.getLogger('dscience')

class JsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, np.ndarray):
			return obj.tolist()
		elif isinstance(obj, (datetime, date)):
			return obj.isoformat()
		return json.JSONEncoder.default(self, obj)

V = TypeVar('V')
class LazyWrapped(Generic[V], metaclass=abc.ABCMeta):

	def __init__(self):
		self._v, self._exists = None, False

	def get(self) -> V:
		if not self._exists:
			self._v = self._generate()
			self._exists = True
		return self._v

	@property
	def raw_value(self):
		return self._v

	@property
	def is_defined(self):
		return self._exists

	@property
	def _name(self):
		raise NotImplementedError()

	def _generate(self):
		raise NotImplementedError()

	def __repr__(self):
		return self._name + '[' + (repr(self._v) if self.is_defined else '⌀') + ']'
	def __str__(self):
		return self._name + '[' + (str(self._v) if self.is_defined else '⌀') + ']'
	def __eq__(self, other):
		return type(self) == type(other) and self.is_defined == other.__exists and type(self._v) == type(other.__v) and self._v == other.__v


class PlainLazyWrapped(LazyWrapped, metaclass=abc.ABCMeta):
	pass

class ClearableLazyWrapped(LazyWrapped, metaclass=abc.ABCMeta):
	def clear(self) -> None:
		self._exists = False


class LazyWrap:

	@classmethod
	def new_type(cls, dtype: str, generator: Callable[[], V]) -> Type[PlainLazyWrapped]:
		# noinspection PyTypeChecker
		return cls._new_type(dtype, generator, PlainLazyWrapped)

	@classmethod
	def new_clearable_type(cls, dtype: str, generator: Callable[[], V]) -> Type[ClearableLazyWrapped]:
		# noinspection PyTypeChecker
		return cls._new_type(dtype, generator, ClearableLazyWrapped)

	@classmethod
	def _new_type(cls, dtype: str, generator: Callable[[], V], superclass: Type[LazyWrapped]) -> Type[LazyWrapped]:
		"""
		Creates a new mutable wrapped type.
		For ex:
		```
		LazyRemoteTime = LazyWrap.new_type('RemoteTime', lambda: urllib...)
		dt = LazyRemoteTime()  # nothing happens
		print(dt.get())  # has a value
		```
		:param dtype: The name of the data type, such as 'datetime' if generator=datetime.now
		:param generator: This is called to (lazily) initialize an instance of the LazyWrapped
		:return: A new class subclassing LazyWrapped
		"""
		class X(superclass):
			@property
			def _name(self):
				return dtype
			def _generate(self):
				return generator()
		X.__name__ = superclass.__name__ + dtype
		return X


class SmartEnum(enum.Enum):
	"""
	An enum with a classmethod `of` that parses a string of the member's name.
	"""
	@classmethod
	def of(cls, v):
		"""
		Returns the member of this enum class from a string with the member's name, case-insentive and stripping whitespace.
		Will return `v` if `v` is already an instance of this class.
		"""
		if isinstance(v, cls):
			return v
		elif isinstance(v, str):
			if v in cls:
				return cls[v.upper().strip()]
			else:
				# in case the names are lowercase
				# noinspection PyTypeChecker
				for e in cls:
					if e.name.lower().strip() == v:
						return e
				raise LookupError("{} not found in {}".format(v, str(cls)))
		else:
			raise TypeError(str(type(v)))

# noinspection PyPep8Naming
class frozenlist(Sequence):
	"""
	An immutable sequence backed by a list.
	The sole advantage over a tuple is the list-like __str__ with square brackets, which may be less confusing to a user.
	"""
	def __init__(self, items: Iterable[T]):
		self.__items = list(items)

	def __getitem__(self, item) -> T:
		if isinstance(item, int):
			return self.__items[item]
		else:
			return frozenlist(self.__items[item])

	def __setitem__(self, key, value):
		raise ImmutableError()

	def __len__(self) -> int:
		return len(self.__items)

	def __repr__(self):
		return repr(self.__items)

	def __eq__(self, other):
		return type(self) == type(other) and self.__items == other.__items

	def __str__(self):
		return repr(self.__items)


class OptRow:
	"""
	Short for 'optional row'.
	A wrapper around a NamedTuple that returns None if the key doesn't exist.
	This is intended for Pandas itertuples().
	"""
	def __init__(self, row):
		self._row = row

	def __getattr__(self, item: str) -> Any:
		try:
			return getattr(self._row, item)
		except AttributeError:
			return None

	def opt(self, item: str, look=None) -> Any:
		x = getattr(self, item)
		if x is None: return None
		return _look(x, look)

	def req(self, item: str, look=None) -> Any:
		x = getattr(self._row, item)
		if x is None: return None
		return _look(x, look)

	def __contains__(self, item):
		try:
			getattr(self._row, item)
			return True
		except AttributeError:
			return False

	def items(self):
		# noinspection PyProtectedMember
		return self._row._asdict()

	def keys(self):
		# noinspection PyProtectedMember
		return self._row._asdict().keys()

	def values(self):
		# noinspection PyProtectedMember
		return self._row._asdict().values()

	def __repr__(self):
		return self.__class__.__name__ + '@' + hex(id(self))

	def __str__(self):
		return self.__class__.__name__

	def __eq__(self, other):
		# noinspection PyProtectedMember
		return self._row == other._row


__version__ = '0.1.0'
__all__ = ['JsonEncoder', 'SmartEnum', 'frozenlist', 'PathLike', 'OptRow', 'LazyWrap']
