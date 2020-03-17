import pytest
from dscience.core.exceptions import *
raises = pytest.raises
E = HashValidationFailedError

class TestExceptions:

	def test_args(self):
		assert hasattr(E(), 'key')
		assert E().key is None
		assert E('abc').key is None
		assert E('abc', key=5).key == 5

	def test_str(self):
		assert str(E()) == ''
		assert str(E(key=5)) == ''
		assert str(E('asdf')) == 'asdf'
		assert str(E('asdf', key=5)) == 'asdf'

	def test_info(self):
		assert E('abc', key=5).info() == 'HashValidationFailedError:abc(expected=None,actual=None,key=5)'

	def test_equality(self):
		assert E() == E()
		assert E() is not E()
		assert E() != E(key=5)
		assert E(key=5) == E(key=5)
		assert E('a', key=5) == E('a', key=5)
		assert E(key=5) != E('a', key=5)
		assert E('a', key=5) != E('a')
		assert E('a') == E('a')


if __name__ == '__main__':
	pytest.main()
