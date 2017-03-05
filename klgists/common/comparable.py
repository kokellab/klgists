class Comparable:
	"""A class that's comparable. Just implement __lt__. Credit ot Alex Martelli on https://stackoverflow.com/questions/1061283/lt-instead-of-cmp"""

	def __eq__(self, other):
		return not self < other and not other < self

	def __ne__(self, other):
		return self < other or other < self

	def __gt__(self, other):
		return other < self

	def __ge__(self, other):
		return not self < other

	def __le__(self, other):
		return not other < self
