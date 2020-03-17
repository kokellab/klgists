import pytest
from io import StringIO
from dscience.core.io import *
from dscience.core.mocks import *

class TestIo:
	def test_delegating(self):
		a, b = MockWritable(), MockWritable()
		d = DelegatingWriter(a, b)
		d.write('abc')
		assert a.data == 'write:abc'
		assert b.data == 'write:abc'
		d.flush()
		assert a.data == 'write:abcflush'
		assert b.data == 'write:abcflush'
		d.close()
		assert a.data == 'write:abcflushclose'
		assert b.data == 'write:abcflushclose'
		a.write('00')
		assert a.data == 'write:00'
		assert b.data == 'write:abcflushclose'

	def test_capture(self):
		w = StringIO('abc')
		c = Capture(w)
		assert c.value == 'abc'

if __name__ == '__main__':
	pytest.main()

