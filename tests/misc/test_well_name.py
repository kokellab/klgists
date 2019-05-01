import pytest
from typing import Iterator, Sequence, Set
from hypothesis import given
from hypothesis.strategies import integers
import re

from klgists.misc.well_name import *
from klgists.misc.well_name import WbFactory, well_name, wells_of_row, well_index_from_name


class TestWellBase:

	@given(integers(min_value=0, max_value=30), integers(min_value=0, max_value=30), integers(min_value=0, max_value=30))
	def test_build(self, base: int, n_rows: int, n_columns: int):
		if n_rows < base or n_columns < base:
			return  # TODO better
		wb = WbFactory.new(base)(n_rows, n_columns)
		assert (wb.n_rows, wb.n_columns) == (n_rows, n_columns)
		assert wb.n_wells == n_rows*n_columns
		assert len(wb.all_indices()) == n_rows*n_columns
		if n_rows*n_columns > 0:
			first = next(iter(wb.all_indices()))
			assert first == base
			first_label = wb.index_to_label(first)
			assert wb.label_to_index(first_label) == base
			first_rc = wb.index_to_rc(first)
			assert first_rc == (base, base)
			assert wb.rc_to_index(*first_rc) == first

	@given(integers(min_value=0, max_value=95))
	def test_index_to_label_wb096(self, index: int):
		wb = WB0(8, 12)
		assert wb.label_to_index(wb.index_to_label(index)) == index

	@given(integers(min_value=1, max_value=96))
	def test_index_to_label_wb196(self, index: int):
		wb = WB1(8, 12)
		assert wb.label_to_index(wb.index_to_label(index)) == index

	def test_ranges(self):
		wb = WB1(4, 4)
		assert list(wb.simple_range('A01', 'D01')) == ['A01', 'B01', 'C01', 'D01']
		assert list(wb.block_range('A01', 'C02')) == ['A01', 'A02', 'B01', 'B02', 'C01', 'C02']
		assert list(wb.traversal_range('A01', 'B02')) == ['A01', 'A02', 'A03', 'A04', 'B01', 'B02']

	def test_simple(self):

		assert well_name(0) == 'A01'
		assert well_name(-1) == 'H12'
		assert well_name(-15) == 'G10'
		assert wells_of_row(0, n_columns=4) == ['A01', 'A02', 'A03', 'A04']
		assert wells_of_row(0, n_columns=2) == ['A01', 'A02']
		assert wells_of_row(3, n_columns=2) == ['D01', 'D02']
		assert wells_of_row(13, n_rows=14, n_columns=2) == ['N01', 'N02']
		assert wells_of_row(2, n_columns=200)[-1] == 'C200'
		assert [well_index_from_name(x) for x in ['A01', 'H12', 'G10']] == [0, 95, 81]
		assert [well_index_from_name(x, n_columns=4) for x in ['A01', 'A02', 'A03', 'A04']] == [0, 1, 2, 3]
