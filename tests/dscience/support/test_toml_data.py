import pytest
from dscience.support.toml_data import *

class TestTomlData:
	def test(self):
		t = TomlData({'a': '0', 'b': 1, 'c': {'c1': 8, 'c2': ['abc', 'xyz']}})
		assert list(t.keys()) == ['a', 'b', 'c']


if __name__ == '__main__':
	pytest.main()

