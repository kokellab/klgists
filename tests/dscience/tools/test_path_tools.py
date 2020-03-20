import pytest
from dscience.core.exceptions import FileDoesNotExistError
from dscience.tools.path_tools import *


class TestPathTools:

	def test_sanitize_filename(self):
		assert 'abc_xyz' == str(PathTools.sanitize_file_path('abc|xyz', False))
		assert 'abc\\xyz' == str(PathTools.sanitize_file_path('abc\\xyz.', False))
		assert 'xyz' == str(PathTools.sanitize_file_path('xyz...', False))
		assert 'abc\\xyz\\n' == str(PathTools.sanitize_file_path('abc\\.\\xyz\\n.', False))
		with pytest.raises(FileDoesNotExistError):
			PathTools.sanitize_file_path('x' * 255)
		with pytest.raises(FileDoesNotExistError):
			PathTools.sanitize_file_path('NUL')
		with pytest.raises(FileDoesNotExistError):
			PathTools.sanitize_file_path('abc\\NUL')
		with pytest.raises(FileDoesNotExistError):
			PathTools.sanitize_file_path('NUL\\abc')


if __name__ == '__main__':
	pytest.main()
