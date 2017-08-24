# coding=utf-8

def zip_strict(*args):
	"""Same as zip(), but raises a ValueError if the lengths don't match."""
	iters = [iter(axis) for axis in args]
	n_elements = 0
	failures = []
	while len(failures) == 0:
		n_elements += 1
		values = []
		failures = []
		for axis, iterator in enumerate(iters):
			try:
				values.append(next(iterator))
			except StopIteration:
				failures.append(axis)
		if len(failures) == 0:
			yield tuple(values)
	if len(failures) == 1:
		raise ValueError("Too few elements ({}) along axis {}".format(n_elements, failures[0]))
	elif len(failures) < len(iters):
		raise ValueError("Too few elements ({}) along axes {}".format(n_elements, failures))
