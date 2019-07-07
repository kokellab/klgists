import pytest
from typing import Iterator, Sequence, Set
from hypothesis import given
from hypothesis.strategies import integers
import re

from klgists.misc.well_name import *
from klgists.misc.well_name import WbFactory


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

	def test_parse(self):
		wb = ParsingWB1(4, 4)
		assert wb.parse("A01-C01") == ['A01', 'B01', 'C01']
		assert wb.parse("A1-C1") == ['A01', 'B01', 'C01']
		assert wb.parse("A01...A03") == ['A01', 'A02', 'A03']
		assert wb.parse("A01-A04") == ['A01', 'A02', 'A03', 'A04']
		assert wb.parse("A01...B02") == ['A01', 'A02', 'A03', 'A04', 'B01', 'B02']
		assert wb.parse("A01*B02") == ['A01', 'A02', 'B01', 'B02']

