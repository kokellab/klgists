import os
from itertools import chain

def flatmap(func, *iterable):
	return chain.from_iterable(map(func, *iterable))

def flatten(*iterable):
	return list(chain.from_iterable(iterable))

class DevNull:
	def write(self, msg): pass

pjoin = os.path.join
