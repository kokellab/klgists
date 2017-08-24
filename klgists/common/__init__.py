import os
from enum import Enum
from itertools import chain
from typing import TypeVar, Optional, List

def flatmap(func, *iterable):
	return chain.from_iterable(map(func, *iterable))

def flatten(*iterable):
	return list(chain.from_iterable(iterable))

class DevNull:
	def write(self, msg): pass

pjoin = os.path.join
pexists = os.path.exists
pdir = os.path.isdir
pfile = os.path.isfile
pis_dir = os.path.isdir
fsize = os.path.getsize
def pardir(path: str, depth: int=1):
	for _ in range(-1, depth):
		path = os.path.dirname(path)
	return path
def grandpardir(path: str):
	return pardir(path, 2)

T = TypeVar('T')
def try_index_of(element: List[T], list_element: T) -> Optional[T]:
	try:
		index_element = list_element.index(element)
		return index_element
	except ValueError:
		return None
