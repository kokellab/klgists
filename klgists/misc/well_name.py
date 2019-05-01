import itertools
from functools import partial
import typing
from typing import List, Iterable, Iterator, Sequence, Type

from klgists.common import abcd
from klgists.common.exceptions import OutOfRangeError


def well_name(index: int, n_rows: int=8, n_columns: int=12) -> str:
	"""Returns a 3-character well identifier like A52. Note that the default is landscape indexing (8 rows and 12 columns).
	Limited to plates with no more than 26 rows.
	Modified from https://stackoverflow.com/questions/19170420/converting-well-number-to-the-identifier-on-a-96-well-plate.
	"""
	index = int(index)
	if n_rows > 52:  # a 1536-well plate has 32 rows and 48 columns, so this won't work with that
		raise OutOfRangeError('Well names are limited to plates with 26 rows!')
	if index >= n_rows * n_columns:
		raise OutOfRangeError('Well index {} is out of range (max is {})'.format(index, n_rows*n_columns))
	return [chr(i) for i in range(0x41, 0x41 + n_rows)][index // n_columns] + '%02d' % (index % n_columns + 1,)

def wells_of_row(row_index: int, n_rows: int=8, n_columns: int=12) -> List[str]:
	"""Returns an ordered list of well names. row_index starts at 0."""
	return [well_name(i, n_rows=n_rows, n_columns=n_columns) for i in range(row_index*n_columns, (row_index+1)*n_columns)]

def wells_of_rows(row_indices: Iterable[int], n_rows: int=8, n_columns: int=12) -> Iterator[str]:
	"""Returns an ordered list of well names. row_index starts at 0."""
	# surprisingly, this is MUCH faster than a for loop and list.extend
	return itertools.chain.from_iterable(map(partial(wells_of_row, n_rows=n_rows, n_columns=n_columns), row_indices))

def well_index_from_name(name: str, n_rows: int=8, n_columns: int=12) -> int:
	return (ord(name[0])%32)*n_columns - 1 - (n_columns - int(name[1:]))


# these are much faster
standards = {(r, c): [well_name(i, n_rows=r, n_columns=c) for i in range(0, r*c)] for r, c in [(12, 8), (8, 12), (24, 16), (16, 24)]}


@abcd.auto_eq(only=['base', 'n_rows', 'n_columns'])
@abcd.auto_hash(only=['base', 'n_rows', 'n_columns'])
@abcd.total_ordering
class _WB(abcd.ABC):
	"""
	A set of conversion utils between well labels, indices, and coordinates.
	This class is preferred over the functions above.
	Short for "Well Base".
	This superclass is hidden. Use only the subclasses WB0 and WB1.
	"""
	def __init__(self, n_rows: int, n_columns: int):
		self.n_rows = n_rows
		self.n_columns = n_columns
		self.n_wells = n_rows * n_columns
		self.__well_name0 = lambda i: well_name(i, n_rows, n_columns)
		self.__well_index0 = lambda i: well_index_from_name(i, n_rows, n_columns)
		self.__well_rc0 = lambda i: (i//n_columns, i % n_columns)
		self.__rc_to_i0 = lambda r, c:  self.n_columns*r + c
		self.base = self.get_base()

	@classmethod
	#@abcd.abstractmethod
	def get_base(cls) -> int:
		raise NotImplementedError()

	def label_to_index(self, label: str) -> int:
		return self.__well_index0(label) + self.base

	def label_to_rc(self, label: str) -> typing.Tuple[int, int]:
		r, c = self.__well_rc0(self.__well_index0(label))
		return r + self.base, c + self.base

	def index_to_label(self, i: int) -> str:
		self.__check_index_range(i)
		return self.__well_name0(i - self.base)

	def index_to_rc(self, i: int) -> typing.Tuple[int, int]:
		self.__check_index_range(i)
		r, c = self.__well_rc0(i-self.base)
		return r+self.base, c+self.base

	def rc_to_label(self, row: int, column: int) -> str:
		self.__check_rc_range(row, column)
		i = self.__rc_to_i0(row-self.base, column-self.base)
		return self.__well_name0(i)

	def rc_to_index(self, row: int, column: int) -> int:
		self.__check_rc_range(row, column)
		return self.__rc_to_i0(row-self.base, column-self.base) + self.base

	def all_labels(self) -> Sequence[str]:
		return [self.index_to_label(i) for i in self.all_indices()]

	def all_rcs(self) -> Sequence[typing.Tuple[int, int]]:
		return [self.index_to_rc(i) for i in self.all_indices()]

	def all_indices(self) -> Sequence[int]:
		return list(range(self.base, self.n_rows*self.n_columns+self.base))

	def simple_range(self, a: str, b: str) -> Iterator[str]:
		ar, ac = self.label_to_rc(a)
		br, bc = self.label_to_rc(b)
		if ar == br:
			for c in range(ac, bc + 1):
				yield self.rc_to_label(ar, c)
		elif ac == bc:
			for r in range(ar, br + 1):
				yield self.rc_to_label(r, ac)
		else:
			raise ValueError("{}-{} is not a simple range".format(a, b))

	def block_range(self, a: str, b: str) -> Iterator[str]:
		ar, ac = self.label_to_rc(a)
		br, bc = self.label_to_rc(b)
		for r in range(ar, br + 1):
			for c in range(ac, bc + 1):
				yield self.rc_to_label(r, c)

	def traversal_range(self, a: str, b: str) -> Iterator[str]:
		ai = self.label_to_index(a)
		bi = self.label_to_index(b)
		for i in range(ai, bi + 1):
			yield self.index_to_label(i)

	def __check_rc_range(self, row: int, column: int):
		if row < self.base or row > self.n_rows * self.n_columns or column < self.base or column > self.n_rows * self.n_columns + self.base - 1:
			raise OutOfRangeError("{}-based coordinates {} out of range".format(self.base, (row, column)))

	def __check_index_range(self,i: int):
		if i < self.base or i > self.n_wells + self.base - self.base:
			raise OutOfRangeError("{}-based index {} out of range".format(self.base, i))

	def __lt__(self, other):
		if self.__class__ != other.__class__:
			raise TypeError("Wrong type {}".format(type(other)))
		if self.n_wells < other.n_wells: return True
		if self.n_wells > other.n_wells: return False
		return (self.n_rows, self.n_columns) < (other.n_rows, other.n_columns)

	def __repr__(self):
		return "WB{}({}×{})".format(self.base, self.n_rows, self.n_columns)
	def __str__(self):
		return "WB{}({}×{})".format(self.base, self.n_rows, self.n_columns)


class WbFactory:

	@classmethod
	def new(cls, base: int) -> Type[_WB]:
		new_class = type('WB{}'.format(base), (_WB,), {})
		new_class.get_base = lambda c: base
		return new_class


@abcd.immutable
class WB1(_WB):
	"""
	Map of a plate with conversions between labels, indices, and (row, column) pairs.
	ALL of these methods assume 1-based indices (1 is the first index and (1,1) is the first coordinate).
	"""
	@classmethod
	@abcd.overrides
	def get_base(cls):
		return 1


@abcd.immutable
class WB0(_WB):
	"""
	Map of a plate with conversions between labels, indices, and (row, column) pairs.
	ALL of these methods assume 0-based indices (1 is the first index and (0,0) is the first coordinate).
	The labels still start at A1 (0,0).
	"""
	@classmethod
	@abcd.overrides
	def get_base(cls):
		return 0



__all__ = ['WB1', 'WB0']
