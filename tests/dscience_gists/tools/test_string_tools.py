import pytest
from dscience_gists.tools.string_tools import *


class TestStringTools:

	def test_truncate(self):
		assert '12…' == StringTools.truncate('1234567', 3)
		assert '…' == StringTools.truncate('1234567', 1)
		assert '…' == StringTools.truncate('1234567', 0)
		assert '…' == StringTools.truncate('1234567', -1)
		assert '12…' == StringTools.truncate('1234567', 3)
		assert '123' == StringTools.truncate('123', 3)
		assert '123' == StringTools.truncate('123', 6)
		assert None is StringTools.truncate(None, 4)
		assert '…………' == StringTools.truncate(None, 4, True)

	def fix_greek(self):
		assert StringTools.fix_greek('beta') == u'\u03B2'
		assert StringTools.fix_greek('theta') == u'\u03B8'
		assert StringTools.fix_greek('Beta') == u'\u0392'
		assert StringTools.fix_greek('BETA') == 'BETA'
		assert StringTools.fix_greek('BETA', lowercase=True) == 'BETA'
		assert StringTools.fix_greek('Beta', lowercase=True) == u'\u03B2'

	def test_strip_off(self):
		assert 'abc' == StringTools.strip_off('abs=abc', 'abs=')
		assert 'abc' == StringTools.strip_off('abs=abcabs=', 'abs=')
		assert StringTools.strip_ends('123456', '1', '6')

	def test_tabs_to_list(self):
		assert ['a', 'b', 'c\td', 'e'] == StringTools.tabs_to_list('a\t"b"\t"c\td"\te')


if __name__ == '__main__':
	pytest.main()
