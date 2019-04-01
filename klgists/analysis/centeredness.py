# Douglas Myers-Turnbull wrote this for the Kokel Lab, which has released it under the Apache Software License, Version 2.0
# See the license file here: https://gist.github.com/dmyersturnbull/bfa1c3371e7449db553aaa1e7cd3cac1
# The list of copyright owners is unknown

import numpy as np

def centeredness(data: np.ndarray) -> np.float64:
	"""A measure of how much the data is concentrated toward the center of a multidimensional array.
	Could probably be defined better. centeredness(arr) == centeredness(arr * 100),
	but centeredness values for arrays of different sizes are not comparable.
	Returns NaN for an empty array."""
	epsilon = np.finfo(np.float64).resolution
	if data.size == 0:
		return float('NaN')
	def w(*indices):
		val = 1
		for axis, length in enumerate(data.shape):
			val *= (indices[axis] + 1)**2 * (length - indices[axis])**2
		return val
	data = data.astype(np.float64)
	data /= (float(data.max() - data.min())) + epsilon
	weight = np.fromfunction(w, data.shape)
	# max value has all the positive values in the center and all the negative in the corner
	mx = (weight.max() * data[data > 0]).sum() + (weight.min() * data[data < 0]).sum()
	return np.asarray(np.sum(data * weight) / mx)


__all__ = ['centeredness']
