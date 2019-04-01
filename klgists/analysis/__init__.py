import numpy as np


def sliding_window(x: np.ndarray, n: int) -> np.ndarray:
	"""Returns a sliding window of n elements from x.
	Raises a ValueError of n > len(x).
	"""
	if n > len(x): raise ValueError("N must be less than the array length")
	# Courtesy of https://stackoverflow.com/questions/13728392/moving-average-or-running-mean
	return np.convolve(x, np.ones((n,)) / n, mode='valid')


__all__ = ['sliding_window']
