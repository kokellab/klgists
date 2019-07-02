import typing
from typing import Iterator, Sequence, Type

from klgists.common import abcd
from klgists.common.exceptions import OutOfRangeError


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


class WB1(_WB):
	"""
	Map of a plate with conversions between labels, indices, and (row, column) pairs.
	ALL of these methods assume 1-based indices (1 is the first index and (1,1) is the first coordinate).
	"""
	@classmethod
	@abcd.overrides
	def get_base(cls):
		return 1


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
