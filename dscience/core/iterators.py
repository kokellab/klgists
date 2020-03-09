from typing import Generic, TypeVar, Iterable, Any
import abc
import collections
import numpy as np
T = TypeVar('T')
IX = TypeVar('IX')


# noinspection PyAbstractClass
class SizedIterator(collections.abc.Iterator, metaclass=abc.ABCMeta):
	"""
	An iterator with size and progress.
	"""

	def position(self) -> int:
		raise NotImplementedError()

	def total(self) -> int:
		raise NotImplementedError()

	def remaining(self) -> int:
		return self.total() - self.position()

	def has_next(self) -> bool:
		return self.position() < self.total()

	def __len__(self) -> int:
		return self.total()

	def __repr__(self):
		return "{}({} items)".format(self.__class__, self.total())

	def __str__(self): return repr(self)


class SeqIterator(SizedIterator, Generic[IX]):
	"""
	A concrete SizedIterator backed by a list.
	"""
	def __init__(self, it: Iterable[Any]):
		self.seq, self.__i, self.current = list(it), 0, None

	def reset(self) -> None:
		self.__i, self.current = 0, None

	def peek(self) -> None:
		return self.seq[self.__i]

	def position(self) -> int:
		return self.__i

	def total(self) -> int:
		return len(self.seq)

	def __next__(self) -> T:
		try:
			self.current = self.seq[self.__i]
		except IndexError:
			raise StopIteration("Size is {}".format(len(self)))
		self.__i += 1
		return self.current


class TieredIterator(SeqIterator):
	"""
	A SizedIterator that iterates over every tuples of combination from multiple sequences.
	Ex:
	it = TieredIterator([[1, 2, 3], [5, 6]])
	list(it)  # [(1,5), (1,6), (2,5), (2,6), (3,5), (3,6)]
	"""
	# noinspection PyMissingConstructor
	def __init__(self, sequence):
		self.seqs = list([SeqIterator(s) for s in reversed(sequence)])
		self.__total = 0 if len(self.seqs) == 0 else int(np.product([i.total() for i in self.seqs]))
		self.__i = 0

	def position(self) -> int:
		return self.__i

	def total(self) -> int:
		return self.__total

	def __next__(self):
		if not self.has_next():
			raise StopIteration("Length is {}".format(self.total()))
		t = tuple((seq.peek() for seq in reversed(self.seqs)))
		self.__set(0)
		self.__i += 1
		return t

	def __set(self, i: int):
		seq = self.seqs[i]
		if seq.remaining() > 1:
			next(seq)
		else:
			seq.reset()
			if i < len(self.seqs) - 1:  # to avoid index error for last case, after which self.has_next() is False
				self.__set(i+1)  # recurse

	def __repr__(self):
		return "{}({} items)".format(self.__class__.__name__, [it.total() for it in self.seqs])

	def __str__(self): return repr(self)


__all__ = ['SizedIterator', 'SeqIterator', 'TieredIterator']
