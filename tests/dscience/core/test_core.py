import pytest
from dscience.core import frozenlist, PathLike, OptRow
from dscience.core.exceptions import ImmutableError
raises = pytest.raises

class TestCore:

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

