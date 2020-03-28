import pytest
from datetime import datetime
from dscience.support.templates import *

class TestTemplates:
	def test(self):
		assert MagicTemplate.from_text('abc ${{x}}').add('x', 1).parse() == 'abc 1'
		assert MagicTemplate.from_text('abc ${{minor}} ${{major}} ${{patch}}').add_version('1.3.9').parse() == 'abc 3 1 9'
		at = datetime(2001, 2, 2)
		assert MagicTemplate.from_text('abc ${{datetuple}}').add_datetime(at).parse() == 'abc (2001, 2, 2)'
		assert MagicTemplate.from_text('abc ${{datetuple}}').add_datetime().parse().startswith('abc')


if __name__ == '__main__':
	pytest.main()

