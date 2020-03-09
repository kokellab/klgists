import pytest
from hypothesis import given
from hypothesis import strategies
from dscience.tools.string_tools import *
from dscience.core.chars import *
from dscience.core.mocks import *
raises = pytest.raises

class TestStringTools:

	def test_pretty_dict(self):
		f = StringTools.pretty_dict
		assert f({'☢': '☡'}) == '{\n\t"☢": "☡"\n}'

	def test_retab(self):
		f = StringTools.retab
		assert f('abc 123\n' + ' '*5 + 'abc\n' + ' '*6 + '\n', 3) == 'abc 123\n' + '\t' + ' '*2 + 'abc\n' + '\t'*2 + '\n'

	def test_strip_empty_decimal(self):
		f = StringTools.strip_empty_decimal
		assert f('5.2') == '5.2'
		assert f('5.0') == '5'
		assert f(5.0) == '5'
		assert f(5) == '5'
		assert f(1E-10) == str(1E-10)
		with raises(TypeError):
			# noinspection PyTypeChecker
			f([1])

	def test_truncate(self):
		f = StringTools.truncate
		assert '12…' == f('1234567', 3)
		assert '…' == f('1234567', 1)
		assert '…' == f('1234567', 0)
		assert '…' == f('1234567', -1)
		assert '12…' == f('1234567', 3)
		assert '123' == f('123', 3)
		assert '123' == f('123', 6)
		assert None is f(None, 4)
		assert '…………' == f(None, 4, True)

	def fix_greek(self):
		f = StringTools.fix_greek
		assert f('beta') == u'\u03B2'
		assert f('theta') == u'\u03B8'
		assert f('Beta') == u'\u0392'
		assert f('BETA') == 'BETA'
		assert f('BETA', lowercase=True) == 'BETA'
		assert f('Beta', lowercase=True) == u'\u03B2'

	def test_strip_off(self):
		f = StringTools.strip_off
		assert 'abc' == f('abs=abc', 'abs=')
		assert 'abc' == f('abs=abcabs=', 'abs=')

	def test_ends(self):
		f = StringTools.strip_ends
		assert f('123456', '1', '6')

	def test_tabs_to_list(self):
		assert ['a', 'b', 'c\td', 'e'] == StringTools.tabs_to_list('a\t"b"\t"c\td"\te')

	def test_longest_str(self):
		f = StringTools.longest_str
		assert f(['1', 'abc', 'xyz', '2']) == 'abc'

	def test_strip_brackets(self):
		f = StringTools.strip_brackets
		assert f('{{[(abcd]}}') == '(abcd'
		assert f('{[{abcd}]}') == 'abcd'
		assert f('') == ''

	def test_strip_paired(self):
		f = StringTools.strip_paired
		assert f('{{[(abcd]}}', [('a', 'b')]) == '{{[(abcd]}}'
		assert f('abcd', [('a', 'b')]) == 'abcd'
		assert f('abab', [('a', 'b')]) == 'ba'
		assert f('aabb', [('a', 'b')]) == ''
		assert f('', []) == ''

	@given(strategies.integers())
	def test_subscript_ints(self, i: int):
		assert StringTools.unsubscript(StringTools.subscript(str(i))) == str(i)

	@given(strategies.text())
	def test_subscript_strs(self, s: str):
		assert StringTools.unsubscript(StringTools.subscript(s)) == s

	@given(strategies.text())
	def test_subscript_strs_rev(self, s: str):
		pass # TODO
		#assert StringTools.subscript(StringTools.unsubscript(s)) == s

	@given(strategies.integers())
	def test_superscript_ints(self, i: int):
		assert StringTools.unsuperscript(StringTools.superscript(str(i))) == str(i)

	@given(strategies.text())
	def test_superscript_strs(self, s: str):
		assert StringTools.unsuperscript(StringTools.superscript(s)) == s

	@given(strategies.text())
	def test_superscript_strs_rev(self, s: str):
		pass # TODO
		#assert StringTools.superscript(StringTools.unsuperscript(s)) == s

	def test_dashes_to_hm(self):
		assert StringTools.dashes_to_hm('-——') == '---'

	def test_pretty_float(self):
		f = StringTools.pretty_float
		assert f(0.1) == '+0.1'
		assert f(-0.1) == Chars.minus + '0.1'
		assert f(0.0000001) == '+e−07'
		assert f(0.0) == '0.0'
		assert f(0.1, n_sigfigs=1) == '+0.1'
		assert f(float('NaN')) == Chars.null
		assert f(float('Inf')) == '+' + Chars.inf
		assert f(-float('Inf')) == Chars.minus + Chars.inf
		assert f(0) == '0'
		assert f(1111111) == '+111100'
		with raises(ValueError):
			f(0.0, n_sigfigs=0)

	def test_pretty_function(self):
		f = StringTools.pretty_function
		assert f(lambda: None) == '⟨λ(0)⟩'
		assert f(lambda q: None) == '⟨λ(1)⟩'
		assert f(None) == '⌀'
		assert f(5) == '5'
		def x(): pass
		assert f(x) == '⟨x⟩'
		class X: pass
		class Y:
			def __str__(self): return '!!'
		assert f(X) == '⟨type:X⟩'
		assert f(X()) == '⟨X⟩'
		assert f(Y()) == '!!'
		assert f(Mammal('cat')) == '⟨<cat>|⟩'


if __name__ == '__main__':
	pytest.main()
