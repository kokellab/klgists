import pytest
from dscience.biochem.tissue_expression import *

class TestTissueExpression:
	def test(self):
		t = TissueTable.load()
		assert len(t) > 0
		assert t.tissue('MKNK2')


if __name__ == '__main__':
	pytest.main()

