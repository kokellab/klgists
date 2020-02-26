import pytest
import os
from dscience_gists.core.exceptions import ParsingError
from dscience_gists.tools.filesys_tools import FilesysTools

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
		assert (
			dict(FilesysTools.read_properties_file(load('lines.lines'))) ==
			{
				'line1': '5',
				'line2': '5',
				'line4': 'a'
			}
		)
		with pytest.raises(ParsingError):
			FilesysTools.read_properties_file(load('bad1.properties'))
		with pytest.raises(ParsingError):
			FilesysTools.read_properties_file(load('bad2.properties'))


if __name__ == '__main__':
	pytest.main()
