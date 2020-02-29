import pytest
import numpy as np
from dscience_gists.core.exceptions import MultipleMatchesError, LengthMismatchError
from dscience_gists.tools.base_tools import *
from dscience_gists.support.mocks import *
raises = pytest.raises


class TestBaseTools:

	def test_is_lambda(self):
		f = BaseTools.is_lambda
		assert f(lambda: None)
		assert f(lambda x: None)
		assert f(lambda x, y: None)
		assert not f(None)
		def yes(): return None
		assert not f(yes)
		class X: pass
		assert not f(X())
		assert not f(X)
		assert not f(1)

	def test_only(self):
		only = BaseTools.only
		with raises(TypeError):
			# noinspection PyTypeChecker
			only(1)
		assert only(['a']) == 'a'
		assert only('a') == 'a'
		assert only({'ab'}) == 'ab'
		with raises(MultipleMatchesError):
			only(['a', 'b'])
		with raises(MultipleMatchesError):
			only('ab')
		with raises(LookupError):
			only([])
		with raises(LookupError):
			only('')

	def test_zip_strict(self):
		with raises(TypeError):
			# noinspection PyTypeChecker
			list(BaseTools.zip_strict(1))
		with raises(TypeError):
			# noinspection PyTypeChecker
			len(BaseTools.zip_strict([1, 2], [3, 4]))
		assert len(BaseTools.zip_list([1, 2], [3, 4])) == 2
		assert len(BaseTools.zip_list()) == 0
		for z in (BaseTools.zip_strict, BaseTools.zip_list):
			assert list(z([1, 2], [3, 4])) == [(1, 3), (2, 4)]
			assert list(z()) == []
			assert list(z([])) == []
			with raises(LengthMismatchError):
				list(z([1], [2, 3]))
			with raises(LengthMismatchError):
				list(z([1, 2], [3]))
			with raises(LengthMismatchError):
				list(z([1], []))

	def test_to_true_iterable(self):
		f = BaseTools.to_true_iterable
		assert f(1) == [1]
		assert f('abc') == ['abc']
		assert f(bytes(5)) == [bytes(5)]
		assert f([1, 2]) == [1, 2]
		assert f(list(np.array([1, 2]))) == list(np.array([1, 2]))

	def test_look(self):
		f = BaseTools.look
		with raises(TypeError):
			# noinspection PyTypeChecker
			f(1, 1)
		assert f(Mammal('cat'), 'species') == 'cat'
		assert f(Mammal('cat'), 'owner') is None
		#assert f(Mammal(Mammal('cat')), 'species') == Mammal('cat')
		assert f(Mammal(Mammal('cat')), 'species.species') == 'cat'
		assert str(f(Mammal(Mammal('cat')), 'species')) == '<cat>|'
		assert f(Mammal(Mammal('cat')), lambda m: m.species.species) == 'cat'

	def test_get_log_function(self):
		f = BaseTools.get_log_function
		assert str(f(None)) == '<bound method Logger.info of <Logger dscience_gists (WARNING)>>'
		assert str(f('WARNING')) == '<bound method Logger.warning of <Logger dscience_gists (WARNING)>>'
		assert str(f(10)) == '<bound method Logger.debug of <Logger dscience_gists (WARNING)>>'
		w = MockWritable()
		f(w)('testing')
		assert w.data == 'write:testing'
		w = MockCallable()
		f(w)('testing')
		assert w.data == 'call:testing'
		w = WritableWritableCallable()
		f(w)('testing')
		assert w.data == 'call:testing'


if __name__ == '__main__':
	pytest.main()
