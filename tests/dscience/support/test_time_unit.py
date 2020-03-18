import pytest
from dscience.support.time_unit import *

class TestTimeUnit:

	def test(self):
		# TODO incomplete coverage
		assert TimeUnits.of('s').n_ms == TimeUnits.of('sec').n_ms == TimeUnits.of('second').n_ms
		assert TimeUnits.HOUR.n_ms == 60*60*TimeUnits.SEC.n_ms == 60*60*1000
		assert TimeUnits.WEEK.n_ms == 7*TimeUnits.DAY.n_ms == 604800000

if __name__ == '__main__':
	pytest.main()

