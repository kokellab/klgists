from typing import TypeVar, Optional, Iterator, Dict, Callable, Iterable, Generic, List
from datetime import datetime
import operator, logging
import sys
import numpy as np
from hurry.filesize import size as _hurry
from psutil import virtual_memory
import pandas as pd


K = TypeVar('K')

class FacadePolicy(Generic[K]):

	def should_archive(self) -> bool:
		raise NotImplementedError()

	def can_archive(self) -> bool:
		raise NotImplementedError()

	def reindex(self, items: Dict[K, pd.DataFrame]) -> None:
		raise NotImplementedError()

	def items(self) -> Iterator[K]:
		# TODO this is not overloaded!!
		raise NotImplementedError()

	def accessed(self, key: K) -> None:
		pass
	def added(self, key: K, value: pd.DataFrame) -> None:
		pass
	def removed(self, key: K) -> None:
		pass


class MemoryLimitingPolicy(FacadePolicy, Generic[K]):

	def __init__(self, max_memory_bytes: Optional[int] = None, max_fraction_available_bytes: Optional[float] = None):
		self._max_memory_bytes = max_memory_bytes
		self._max_fraction_available_bytes = max_fraction_available_bytes
		self._total_memory_bytes = 0
		self._usage_bytes = {}  # type: Dict[K, int]
		self._last_accessed = {}  # type: Dict[K, datetime]
		self._created = {}  # type: Dict[K, datetime]

	def can_archive(self) -> bool:
		return len(self._last_accessed) > 0

	def should_archive(self) -> bool:
		return (
			self._max_memory_bytes is not None and self._total_memory_bytes > self._max_memory_bytes
			or self._max_fraction_available_bytes is not None and self._total_memory_bytes > virtual_memory().available * self._max_fraction_available_bytes
		)

	def reindex(self, items: Dict[K, pd.DataFrame]) -> None:
		for key in set(self._last_accessed.keys()) - set(items.keys()):
			if key not in items.keys():
				self.removed(key)
		for key, value in items.items():
			self._usage_bytes[key] = sys.getsizeof(value)
		self._total_memory_bytes = np.sum(self._usage_bytes.values())

	def accessed(self, key: K) -> None:
		self._last_accessed[key] = datetime.now()

	def added(self, key: K, value: pd.DataFrame) -> None:
		now = datetime.now()
		self._created[key] = now
		self._last_accessed[key] = now
		self._usage_bytes[key] = sys.getsizeof(value)
		self._total_memory_bytes += self._usage_bytes[key]

	def removed(self, key: K) -> None:
		self._total_memory_bytes -= self._usage_bytes[key]
		del self._last_accessed[key]
		del self._created[key]
		del self._usage_bytes[key]

	def __str__(self):
		available = virtual_memory().available
		return "{}(n={}, {}/{}, {}/{}={}%)".format(
			type(self).__name__,
			len(self._usage_bytes),
			_hurry(self._total_memory_bytes),
			'-' if self._max_memory_bytes is None else _hurry(self._max_memory_bytes),
			_hurry(self._total_memory_bytes),
			'-' if self._max_fraction_available_bytes is None else _hurry(available * self._max_fraction_available_bytes),
			'-' if self._max_fraction_available_bytes is None else np.round(100 * self._total_memory_bytes / (available * self._max_fraction_available_bytes), 3)
		)

	def __repr__(self):
		ordered = list(self.items())
		ss = []
		if len(ordered) > 0:
			current_day = None
			for k in ordered:
				dt = self._last_accessed[k]
				if current_day is None or current_day.date() != dt.date():
					current_day = dt
					ss.append('#' + current_day.strftime('%Y-%m-%d') + '...')
				ss.append("{}:{}@{}".format(k, _hurry(self._usage_bytes[k]), self._last_accessed[k].strftime('%H:%M:%S')))
		return "{}@{}: [{}]".format(str(self), hex(id(self)), ', '.join(ss))


class MemoryLruPolicy(MemoryLimitingPolicy, Generic[K]):
	def items(self) -> Iterator[K]:
		return iter([k for k, v in sorted(self._last_accessed.items(), key=operator.itemgetter(1))])

class MemoryMruPolicy(MemoryLimitingPolicy, Generic[K]):
	def items(self) -> Iterator[K]:
		return iter([k for k, v in reversed(sorted(self._last_accessed.items(), key=operator.itemgetter(1)))])


class DfFacade(Generic[K]):
	def __init__(self, loader: Callable[[K], pd.DataFrame], policy: FacadePolicy):
		self._loader = loader
		self._items = {}  # type: Dict[K, pd.DataFrame]
		self._policy = policy

	def __getitem__(self, key: K) -> pd.DataFrame:
		self._policy.accessed(key)
		if key in self._items:
			return self._items[key]
		else:
			value = self._loader(key)
			logging.debug("Loaded {}".format(key))
			self._items[key] = value
			self._policy.added(key, value)
			self.archive()
			return value
	def __call__(self,  key: K) -> pd.DataFrame:
		return self[key]

	def archive(self, at_least: Optional[int] = None) -> List[K]:
		it = self._policy.items()
		archived = []
		while self._policy.can_archive() and (at_least is not None and len(archived) < at_least or self._policy.should_archive()):
			key = next(it)
			self._policy.removed(key)
			del self._items[key]
			archived.append(key)
			logging.debug("Archived {} items: {}".format(len(archived), archived))
		return archived

	def clear(self) -> None:
		it = self._policy.items()
		while self._policy.can_archive():
			key = next(it)
			self._policy.removed(key)
			del self._items[key]

	def remove(self, key: K) -> None:
		if key in self:
			self._policy.removed(key)
			del self._items[key]

	def __contains__(self, key: K):
		return key in self._items

	def __delitem__(self, key):
		self.remove(key)

	def __repr__(self):
		return "{}({})@{}".format(type(self).__name__, repr(self._policy), hex(id(self)))
	def __str__(self):
		return "{}({})".format(type(self).__name__, self._policy)


__all__ = ['FacadePolicy', 'DfFacade', 'MemoryLimitingPolicy', 'MemoryLruPolicy', 'MemoryMruPolicy']
