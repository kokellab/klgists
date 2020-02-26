from dscience_gists.core.iterators import *

import pytest

class TestIterators:

	def test_seq_iterator(self):
		seq = SeqIterator([1, 2, 3])
		assert seq.position() == 0
		assert seq.remaining() == 3
		assert seq.total() == len(seq) == 3
		assert seq.remaining() == 3
		for i in range(0, 3):
			assert seq.has_next()
			# next
			assert next(seq) == i + 1
			assert len(seq) == seq.total() == 3
			assert seq.position() == i+1
			assert seq.remaining() == 2-i
		# next
		assert not seq.has_next()
		with pytest.raises(StopIteration):
			next(seq)

	def test_tiered_iterator_0(self):
		it = TieredIterator([])
		assert len(it) == 0
		assert list(it) == []

	def test_tiered_iterator_1_empty(self):
		it = TieredIterator([[]])
		assert len(it) == 0
		assert list(it) == []

	def test_tiered_iterator_2_empty(self):
		it = TieredIterator([[],[1]])
		assert len(it) == 0
		assert list(it) == []

	def test_tiered_iterator_1(self):
		it = TieredIterator([[1,2,3]])
		assert len(it) == 3
		assert list(it) == [(1,), (2,), (3,)]

	def test_tiered_iterator_2(self):
		it = TieredIterator([[1,2], [5,6,7]])
		assert len(it) == 2*3
		assert list(it) == [(1,5), (1,6), (1,7), (2,5), (2,6), (2,7)]

	def test_tiered_iterator_3(self):
		it = TieredIterator([[1,2], [5], ['a', 'b']])
		assert len(it) == 2*1*2
		assert list(it) == [(1,5,'a'), (1,5,'b'), (2,5,'a'), (2,5,'b')]


if __name__ == '__main__':
	pytest.main()

