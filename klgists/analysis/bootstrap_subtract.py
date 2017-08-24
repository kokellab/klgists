# coding=utf-8

import pandas as pd
import numpy as np
from typing import Optional

def bootstrap_subtract(X: pd.DataFrame, Y: pd.DataFrame, n_bootstrap_samples: int=200,
		random_seed: Optional[int]=None) -> pd.DataFrame:
	"""Bootstraps over mean(X) - mean(Y).
		X and Y are n*k Pandas DataFrames of k replicates.
		**NOTE:** X and Y must be single-indexed, each with an unnamed index and unnamed columns.
		The DataFrame returned will have columns 'index' and 'value' of length n*n_bootstrap_samples.
	"""

	def _boot() -> pd.DataFrame:
		"""Bootstraps over X and Y individually, takes the mean, and subtracts.
		The DataFrame will have bad column names."""
		X_boot = X.sample(len(X), replace=True, random_state=random_seed).reset_index().drop('index', axis=1)
		Y_boot = Y.sample(len(Y), replace=True, random_state=random_seed).reset_index().drop('index', axis=1)
		return (X_boot.apply(np.mean, axis=0) - Y_boot.apply(np.mean, axis=0)).to_frame().reset_index()

	R = pd.concat([_boot() for _ in range(0, n_bootstrap_samples)])
	R.columns = ['index', 'value']
	return R
