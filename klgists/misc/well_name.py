# coding=utf-8

import itertools
from functools import partial
from typing import List, Iterable, Iterator

def well_name(index: int, n_rows: int=8, n_columns: int=12) -> str:
	"""Returns a 3-character well identifier like A52. Note that the default is landscape indexing (8 rows and 12 columns).
	Limited to plates with no more than 26 rows.
	Modified from https://stackoverflow.com/questions/19170420/converting-well-number-to-the-identifier-on-a-96-well-plate.
	"""
	if n_rows > 52:  # a 1536-well plate has 32 rows and 48 columns, so this won't work with that
		raise ValueError('Well names are limited to plates with 26 rows!')
	if index >= n_rows * n_columns:
		raise ValueError('Well index {} is out of range (max is {})'.format(index, n_rows*n_columns))
	return [chr(i) for i in range(0x41, 0x41 + n_rows)][index // n_columns] + '%02d' % (index % n_columns + 1,)

def wells_of_row(row_index: int, n_rows: int=8, n_columns: int=12) -> List[str]:
	"""Returns an ordered list of well names. row_index starts at 0."""
	return [well_name(i, n_rows=n_rows, n_columns=n_columns) for i in range(row_index*n_columns, (row_index+1)*n_columns)]

def wells_of_rows(row_indices: Iterable[int], n_rows: int=8, n_columns: int=12) -> Iterator[str]:
	"""Returns an ordered list of well names. row_index starts at 0."""
	# surprisingly, this is MUCH faster than a for loop and list.extend
	return itertools.chain.from_iterable(map(partial(wells_of_row, n_rows=n_rows, n_columns=n_columns), row_indices))

def well_index_from_name(well_name: str, n_rows: int=8, n_columns: int=12) -> int:
	return (ord(well_name[0])%32)*n_columns - 1 - (n_columns - int(well_name[1:]))

# tests
assert well_name(0) == 'A01'
assert well_name(-1) == 'H12'
assert well_name(-15) == 'G10'
assert wells_of_row(0, n_columns=4) == ['A01', 'A02', 'A03', 'A04']
assert wells_of_row(0, n_columns=2) == ['A01', 'A02']
assert wells_of_row(3, n_columns=2) == ['D01', 'D02']
assert wells_of_row(13, n_rows=14, n_columns=2) == ['N01', 'N02']
assert wells_of_row(2, n_columns=200)[-1] == 'C200'
assert [well_index_from_name(x) for x in ['A01', 'H12', 'G10']] == [0, 95, 81]
assert [well_index_from_name(x, n_columns = 4) for x in ['A01', 'A02', 'A03', 'A04']] == [0,1,2,3]

# these are much faster
standards = {(r, c): [well_name(i, n_rows=r, n_columns=c) for i in range(0, r*c)] for r, c in [(12, 8), (8, 12), (24, 16), (16, 24)]}
