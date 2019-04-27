import pytest
from typing import Iterator, Sequence, Set
import numpy as np

from klgists.common import *


def load(parts):
	if isinstance(parts, str): parts = [parts]
	return os.path.join(os.path.dirname(__file__), '..', 'resources', 'common', *parts)


class TestCommon:

	def test_read_lines(self):
		assert (
			['line1 = 5', 'line2=5', '', '#line3', 'line4 = a']
			== list(read_lines_file(load('lines.lines')))
		)
		assert (
			['line1 = 5', 'line2=5', 'line4 = a']
			== list(read_lines_file(load('lines.lines'), ignore_comments=True))
		)

	def test_read_properties(self):
		assert (
			{
				'line1': '5',
				'line2': '5',
				'line4': 'a'
			}
			== dict(read_properties_file(load('lines.lines')))
		)
		with pytest.raises(ParsingFailedException):
			read_properties_file(load('bad1.properties'))
		with pytest.raises(ParsingFailedException):
			read_properties_file(load('bad2.properties'))


if __name__ == '__main__':
	pytest.main()

