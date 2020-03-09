import typing, re
from typing import Iterator, Sequence, Type
from dscience_gists.core import abcd
from dscience_gists.core.exceptions import OutOfRangeError


@abcd.auto_eq(only=['base', 'n_rows', 'n_columns'])
@abcd.auto_hash(only=['base', 'n_rows', 'n_columns'])
@abcd.total_ordering
class _WB(abcd.ABC):
	"""
	A set of conversion utils between well labels, indices, and coordinates.
	This class is preferred over the functions above.
	Short for "Well Base".
	This superclass is hidden. Use only the subclasses WB0 and WB1.
	Limited to plates with no more than 26 rows.
	"""
	def __init__(self, n_rows: int, n_columns: int):
		self.base = self.get_base()
		self.n_rows = n_rows
		self.n_columns = n_columns
		self.n_wells = n_rows * n_columns
		self.__well_name0 = self._ind_to_label
		self.__well_index0 = self._label_to_ind
		self.__well_rc0 = lambda i: (i//n_columns, i % n_columns)
		self.__rc_to_i0 = lambda r, c:  self.n_columns*r + c

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

	def _ind_to_label(self, index: int) -> str:
		"""Returns a 3-character well identifier like A52. Note that the default is landscape indexing (8 rows and 12 columns).

		Modified from https://stackoverflow.com/questions/19170420/converting-well-number-to-the-identifier-on-a-96-well-plate.
		"""
		index = int(index)
		if self.n_rows > 52:  # a 1536-well plate has 32 rows and 48 columns, so this won't work with that
			raise OutOfRangeError('Well names are limited to plates with 26 rows!')
		if index >= self.n_rows * self.n_columns:
			raise OutOfRangeError('Well index {} is out of range (max is {})'.format(index, self.n_rows * self.n_columns))
		return [chr(i) for i in range(0x41, 0x41 + self.n_rows)][index // self.n_columns] + '%02d' % (index % self.n_columns + 1,)

	def _label_to_ind(self, name: str) -> int:
		return (ord(name[0]) % 32) * self.n_columns - 1 - (self.n_columns - int(name[1:]))


class WbFactory:

	@classmethod
	def new(cls, base: int) -> Type[_WB]:
		new_class = type('WB{}'.format(base), (_WB,), {})
		new_class.get_base = lambda c: base
		# noinspection PyTypeChecker
		return new_class


class ParsingWB(_WB, abcd.ABC):
	"""
	An abstract WB that can parse expressions.
	Usage:
		>>> class ParsingWB1(WB1, ParsingWB): pass
	"""

	_pattern = re.compile(r''' *([A-H][0-9]{1,2}) *(?:(-|–|\*|(?:\.\.\.)|…) *([A-H][0-9]{1,2}))? *''')

	def parse(self, expression: str) -> Sequence[str]:
		"""
		Returns the labels from the expression, inclusive.
		Examples:
			A01-A10   (sequence in a single row)
			A01-E01   (sequence in a single column)
			A01*C01   (a rectangular block)
			A01...C01 (a traversal of the wells in order)
		"""
		trav = []
		for txt in expression.split(','):
			trav.extend(self._parse(txt))
		return trav

	def _parse(self, expression: str):
		match = ParsingWB._pattern.fullmatch(expression)
		if match is None:
			raise ValueError("{} is wrong".format(expression))
		a, x, b = match.group(1), match.group(2), match.group(3)
		if x is None:
			return self.simple_range(a, a)
		elif x in {'-', '–'}:
			return self.simple_range(a, b)
		elif x == '*':
			return self.block_range(a, b)
		elif x in {'...', '…'}:
			return self.traversal_range(a, b)
		else:
			assert False, "WHAT?"


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

class ParsingWB0(WB0, ParsingWB): pass
class ParsingWB1(WB1, ParsingWB): pass


__all__ = ['WB1', 'WB0', 'ParsingWB0', 'ParsingWB1', 'WbFactory']
