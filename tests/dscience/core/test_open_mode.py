import pytest
from dscience.core.open_mode import *

class TestOpenMode:
	"""
		- 'r' means read
		- 'w' and 'o' both mean overwrite
		- 'a' means append
		- 's' means "safe" -- complain if it exists (neither overwrite nor append)
		- 'b' means binary
		- 'z' means compressed with gzip; works in both binary and text modes
		- 'd' means detect gzip
	"""

	def test_eq(self):
		o = OpenMode
		assert o('r') == o('r')
		assert o('w') == o('o')
		assert o('w') != o('a')


if __name__ == '__main__':
	pytest.main()

