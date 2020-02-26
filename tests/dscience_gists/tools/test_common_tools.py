import pytest
import numpy as np
from dscience_gists.core.exceptions import MultipleMatchesError, LookupFailedError, LengthMismatchError
from dscience_gists.tools.common_tools import CommonTools

class TestCommon:

	def test_is_empty(self):
		is_empty = CommonTools.is_empty
		assert not is_empty('a')
		assert is_empty([])
		assert not is_empty('None')
		assert is_empty(None)
		assert is_empty('')
		assert is_empty([])
		assert is_empty({})
		assert is_empty(tuple())
		assert not is_empty((5,))
		assert not is_empty(0.0)
		assert not is_empty(np.inf)
		assert is_empty(np.nan)

	def test_is_null(self):
		is_null = CommonTools.is_null
		assert not is_null('a')
		assert not is_null([])
		assert not is_null('None')
		assert not is_null([])
		assert is_null(None)
		assert not is_null('')
		assert not is_null(0.0)
		assert not is_null(np.inf)
		assert is_null(np.nan)

	def test_only(self):
		only = CommonTools.only
		assert only(['a']) == 'a'
		assert only('a') == 'a'
		assert only({'ab'}) == 'ab'
		with pytest.raises(MultipleMatchesError):
			only(['a', 'b'])
		with pytest.raises(MultipleMatchesError):
			only('ab')
		with pytest.raises(LookupFailedError):
			only([])
		with pytest.raises(LookupFailedError):
			only('')

	def test_zip_strict(self):
		for z in [CommonTools.zip_strict, CommonTools.zip_list]:
			assert list(z([1, 2], [3, 4])) == [(1, 3), (2, 4)]
			assert list(z()) == []
			assert list(z([])) == []
			with pytest.raises(LengthMismatchError):
				list(z([1], [2, 3]))
			with pytest.raises(LengthMismatchError):
				list(z([1, 2], [3]))
			with pytest.raises(LengthMismatchError):
				list(z([1], []))

if __name__ == '__main__':
	pytest.main()
