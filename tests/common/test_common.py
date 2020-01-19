import pytest


def load(parts):
	if isinstance(parts, str): parts = [parts]
	return os.path.join(os.path.dirname(__file__), '..', 'resources', 'common', *parts)


class TestCommon:

	def test_only(self):
		assert only(['a']) == 'a'
		assert only('a') == 'a'
		assert only({'ab'}) == 'ab'
		with pytest.raises(MultipleMatchesException):
			only(['a', 'b'])
		with pytest.raises(MultipleMatchesException):
			only('ab')
		with pytest.raises(LookupFailedException):
			only([])
		with pytest.raises(LookupFailedException):
			only('')

	def test_flatten(self):
		assert (
			flatten(*[[1, 2], [3]]) == [1, 2, 3]
		)

	def test_zip_strict(self):
		for z in [zip_strict, zip_strict_list]:
			assert list(z([1, 2], [3, 4])) == [(1, 3), (2, 4)]
			assert list(z()) == []
			assert list(z([])) == []
			with pytest.raises(LengthMismatchError):
				list(z([1], [2, 3]))
			with pytest.raises(LengthMismatchError):
				list(z([1, 2], [3]))
			with pytest.raises(LengthMismatchError):
				list(z([1], []))

	def test_read_lines(self):
		assert (
			list(read_lines_file(load('lines.lines'))) ==
			['line1 = 5', 'line2=5', '', '#line3', 'line4 = a']
		)
		assert (
			list(read_lines_file(load('lines.lines'), ignore_comments=True)) ==
			['line1 = 5', 'line2=5', 'line4 = a']
		)

	def test_read_properties(self):
		assert (
			dict(read_properties_file(load('lines.lines'))) ==
			{
				'line1': '5',
				'line2': '5',
				'line4': 'a'
			}
		)
		with pytest.raises(ParsingFailedException):
			read_properties_file(load('bad1.properties'))
		with pytest.raises(ParsingFailedException):
			read_properties_file(load('bad2.properties'))


if __name__ == '__main__':
	pytest.main()

