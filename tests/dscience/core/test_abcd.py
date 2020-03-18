import pytest
import re
from dscience.core import abcd
raises = pytest.raises
warns = pytest.warns

class TestAbcd:

	def test_auto_obj(self):
		@abcd.auto_obj()
		class X:
			def __init__(self, s):
				self.s = s
		x = X(5)
		assert str(x) == 'X(s=5)'
		assert re.compile(r'X\(s=5 @ 0x[0-9a-h]+\)').fullmatch(repr(x)) is not None, "repr is {}".format(repr(x))
		assert hash(x) == hash((5,))
		assert x == X(5)
		assert x != X(6)

	def test_immutable(self):
		@abcd.immutable
		class X:
			__slots__ = ['s']
			def __init__(self, s):
				self.s = s
		x = X(5)
		with raises(AttributeError):
			x.s = 5

	def test_float_type(self):
		@abcd.float_type('s')
		class X:
			def __init__(self, s):
				self.s = s
		x = X(5)
		# noinspection PyTypeChecker
		assert float(x) == 5.0

	def test_status(self):
		@abcd.status(abcd.CodeStatus.Deprecated)
		def x():
			pass
		with warns(DeprecationWarning):
			x()
		@abcd.status(abcd.CodeStatus.Immature)
		def y():
			pass
		with warns(abcd.ImmatureWarning):
			y()
		@abcd.status(abcd.CodeStatus.Stable)
		def z():
			pass
		with warns(None):
			z()

if __name__ == '__main__':
	pytest.main()
