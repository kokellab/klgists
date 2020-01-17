from klgists.common.tools.gist_tools import GistTools as Tools
from klgists.common.iterators import *
from klgists.common.exceptions import InvalidFileException, MultipleMatchesException

import pytest
import os
import numpy as np

class TestGists:
	"""
	Tests for Tools.
	When running from PyCharm, set the environment variable VALARPY_CONFIG to one for the test database.
	VALARPY_CONFIG=VALARPY_TESTDB_CONFIG
	You can do that in Run...Edit Configuration.
	"""

	def test_seq_iterator(self):
		seq = SeqIterator([1, 2, 3])
		assert seq.position() == 0
		assert seq.remaining() == 3
		assert seq.total() == len(seq) == 3
		assert seq.remaining() == 3
		for i in range(0, 3):
			assert seq.has_next()
			# next
			assert next(seq) == i + 1
			assert len(seq) == seq.total() == 3
			assert seq.position() == i+1
			assert seq.remaining() == 2-i
		# next
		assert not seq.has_next()
		with pytest.raises(StopIteration):
			next(seq)

	def test_tiered_iterator_0(self):
		it = TieredIterator([])
		assert len(it) == 0
		assert list(it) == []

	def test_tiered_iterator_1_empty(self):
		it = TieredIterator([[]])
		assert len(it) == 0
		assert list(it) == []

	def test_tiered_iterator_2_empty(self):
		it = TieredIterator([[],[1]])
		assert len(it) == 0
		assert list(it) == []

	def test_tiered_iterator_1(self):
		it = TieredIterator([[1,2,3]])
		assert len(it) == 3
		assert list(it) == [(1,), (2,), (3,)]

	def test_tiered_iterator_2(self):
		it = TieredIterator([[1,2], [5,6,7]])
		assert len(it) == 2*3
		assert list(it) == [(1,5), (1,6), (1,7), (2,5), (2,6), (2,7)]

	def test_tiered_iterator_3(self):
		it = TieredIterator([[1,2], [5], ['a', 'b']])
		assert len(it) == 2*1*2
		assert list(it) == [(1,5,'a'), (1,5,'b'), (2,5,'a'), (2,5,'b')]

	def test_sanitize_filename(self):
		assert 'abc_xyz' == str(Tools.sanitize_filename('abc|xyz', False))
		assert 'abc\\xyz' == str(Tools.sanitize_filename('abc\\xyz.', False))
		assert 'xyz' == str(Tools.sanitize_filename('xyz...', False))
		assert 'abc\\xyz\\n' == str(Tools.sanitize_filename('abc\\.\\xyz\\n.', False))
		with pytest.raises(InvalidFileException):
			Tools.sanitize_filename('x'*255)
		with pytest.raises(InvalidFileException):
			Tools.sanitize_filename('NUL')
		with pytest.raises(InvalidFileException):
			Tools.sanitize_filename('abc\\NUL')
		with pytest.raises(InvalidFileException):
			Tools.sanitize_filename('NUL\\abc')

	def test_truncate(self):
		assert '12…' == Tools.truncate('1234567', 3)
		assert '…' == Tools.truncate('1234567', 1)
		assert '…' == Tools.truncate('1234567', 0)
		assert '…' == Tools.truncate('1234567', -1)
		assert '12…' == Tools.truncate('1234567', 3)
		assert '123' == Tools.truncate('123', 3)
		assert '123' == Tools.truncate('123', 6)
		assert None is Tools.truncate(None, 4)
		assert '…………' == Tools.truncate(None, 4, True)

	def test_is_empty(self):
		assert not Tools.is_empty('a')
		assert Tools.is_empty([])
		assert not Tools.is_empty('None')
		assert Tools.is_empty(None)
		assert Tools.is_empty('')
		assert Tools.is_empty([])
		assert Tools.is_empty({})
		assert Tools.is_empty(tuple())
		assert not Tools.is_empty((5,))
		assert not Tools.is_empty(0.0)
		assert not Tools.is_empty(np.inf)
		assert Tools.is_empty(np.nan)

	def test_is_null(self):
		assert not Tools.is_null('a')
		assert not Tools.is_null([])
		assert not Tools.is_null('None')
		assert not Tools.is_null([])
		assert Tools.is_null(None)
		assert not Tools.is_null('')
		assert not Tools.is_null(0.0)
		assert not Tools.is_null(np.inf)
		assert Tools.is_null(np.nan)

	def fix_greek(self):
		assert Tools.fix_greek('beta') == u'\u03B2'
		assert Tools.fix_greek('theta') == u'\u03B8'
		assert Tools.fix_greek('Beta') == u'\u0392'
		assert Tools.fix_greek('BETA') == 'BETA'
		assert Tools.fix_greek('BETA', lowercase=True) == 'BETA'
		assert Tools.fix_greek('Beta', lowercase=True) == u'\u03B2'

	def test_only(self):
		assert 'a' == Tools.only(['a'])
		assert 'a' == Tools.only('a')
		assert 1 == Tools.only([1])
		assert 'ab' == Tools.only({'ab'})
		with pytest.raises(MultipleMatchesException):
			Tools.only(['a', 'b'])
		with pytest.raises(MultipleMatchesException):
			Tools.only('ab')
		with pytest.raises(ValueError):
			Tools.only([])
		with pytest.raises(ValueError):
			Tools.only('')

	def test_strip_off(self):
		assert 'abc' == Tools.strip_off('abs=abc', 'abs=')
		assert 'abc' == Tools.strip_off('abs=abcabs=', 'abs=')
		assert Tools.strip_ends('123456', '1', '6')

	def test_tabs_to_list(self):
		assert ['a', 'b', 'c\td', 'e'] == Tools.tabs_to_list('a\t"b"\t"c\td"\te')

	def test_read_properties_file(self):
		path = os.path.join(os.environ['KALE'], 'tests', 'resources', 'core', 'properties.properties')
		data = Tools.read_properties_file(path)
		assert data == {'abc': 'xyz', '123': '1533'}


if __name__ == '__main__':
	pytest.main()

