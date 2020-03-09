from typing import Tuple as Tup
import scipy
from scipy import stats
from statsmodels.nonparametric.kde import KDEUnivariate
import numpy as np
import pandas as pd
from dscience.core.exceptions import LengthMismatchError, NullValueError

class StatTools:

	@classmethod
	def kde(cls, a: np.array, kernel: str = 'gau', bw: str = 'normal_reference') -> Tup[np.array, np.array]:
		"""
		Calculates univariate KDE with statsmodel.
		(This function turned into a thin wrapper around statsmodel.)
		Note that scipy uses statsmodel for KDE if it's available. Otherwise, it silently falls back to scipy. That's clearly hazardous.
		"""
		if isinstance(a, pd.Series):
			a = a.values
		dens = KDEUnivariate(a)
		dens.fit(kernel=kernel, bw=bw)
		return dens.support, dens.density

	@classmethod
	def ttest_pval(cls, z: pd.Series, a: str, b: str) -> float:
		"""Calculates a p-value from a t-test between labels a and b."""
		s = pd.DataFrame(z)
		neg = s[s.index.get_level_values('name') == a].values
		if len(neg) < 2: raise LengthMismatchError("Too few ({}) values for {}".format(len(neg), a), minimum=2)
		pos = s[s.index.get_level_values('name') == b].values
		if len(pos) < 2: raise LengthMismatchError("Too few ({}) values for {}".format(len(pos), b), minimum=2)
		pval = scipy.stats.ttest_ind(pos, neg, equal_var=False).pvalue
		if isinstance(pval, float) and np.isnan(pval): raise NullValueError("NaN for {} and {}".format(a, b))
		else: return pval[0]


__all__ = ['StatTools']
