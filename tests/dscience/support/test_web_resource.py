import pytest
from dscience.core.web_resource import *

class TestWebResource:
	def test(self):
		# TODO incomplete coverage
		t = WebResource('https://www.proteinatlas.org/download/normal_tissue.tsv.zip', 'normal_tissue.tsv', 'tt.txt.gz')
		t.download(redownload=True)
		import pandas as pd
		df = pd.read_csv('tt.txt.gz', sep='\t')
		assert len(df) == 1056061
		assert t.datetime_downloaded()
		assert t.exists()
		t.delete()
		assert not t.exists()


if __name__ == '__main__':
	pytest.main()

