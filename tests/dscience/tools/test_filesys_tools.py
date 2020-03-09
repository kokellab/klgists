import pytest
import os
from dscience.core.exceptions import ParsingError
from dscience.tools.filesys_tools import FilesysTools

def load(parts):
	if isinstance(parts, str): parts = [parts]
	return os.path.join(os.path.dirname(__file__), '..', 'resources', 'common', *parts)


class TestFilesysTools:

	def test_read_lines(self):
		assert (
			list(FilesysTools.read_lines_file(load('lines.lines'))) ==
			['line1 = 5', 'line2=5', '', '#line3', 'line4 = a']
		)
		assert (
			list(FilesysTools.read_lines_file(load('lines.lines'), ignore_comments=True)) ==
			['line1 = 5', 'line2=5', 'line4 = a']
		)

	def test_read_properties(self):
		f = FilesysTools.read_properties_file
		expected = {'line1': '5', 'line2': '5', 'line4': 'a'}
		assert dict(f(load('lines.lines'))) == expected
		with pytest.raises(ParsingError):
			f(load('bad1.properties'))
		with pytest.raises(ParsingError):
			f(load('bad2.properties'))


if __name__ == '__main__':
	pytest.main()
