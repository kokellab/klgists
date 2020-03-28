import pytest
from datetime import datetime
from dscience.core import *
from dscience.core.exceptions import ImmutableError
raises = pytest.raises

class TestCore:

	def test_wrap(self):
		DT = LazyWrap.new_type('datetime', datetime.now)
		dt = DT()
		assert str(dt) == 'datetime[⌀]'
		assert not dt.is_defined
		assert dt.raw_value is None
		v = dt.get()
		assert isinstance(v, datetime)
		assert dt.raw_value == v
		assert dt.is_defined
		a, b = DT(), DT()
		assert a == b
		a.get()
		assert a != b

	def test_frozenlist(self):
		assert frozenlist([1, 2]) == frozenlist([1, 2])
		assert frozenlist([1, 2])[0] == 1
		assert list(frozenlist([1, 2])) == list([1, 2])
		with raises(ImmutableError):
			f = frozenlist([1, 2])
			# noinspection PyUnresolvedReferences
			f[0] = 10

	def test_pathlike(self):
		assert PathLike.isinstance('')
		assert not PathLike.isinstance(5)

	def test_opt_row(self):
		pass  # TODO

if __name__ == '__main__':
	pytest.main()

