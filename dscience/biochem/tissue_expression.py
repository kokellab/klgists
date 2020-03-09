from typing import Callable
from typing import Optional
import pandas as pd
from dscience_gists.core import PathLike
from dscience_gists.support.rezip import Rezipper


class TissueTable:
	"""Contains a Pandas DataFrame of tissue- and cell type-level expression for genes from the Human Protein Atlas.
	Example usage:
		tt = TissueTable()
		tt.tissue('MKNK2') # returns a DataFrame with mean expression of MKNK2 per tissue type. MKN2 is the HGNC symbol.
	"""
	URL = 'http://www.proteinatlas.org/download/normal_tissue.csv.zip'
	DEFAULT_PATH = 'normal_tissue.csv'

	def __init__(self, path: Optional[PathLike] = None):
		self.df = self._load(TissueTable.DEFAULT_PATH if path is None else path)

	def level(self, gene_name: str, group_by: str='Cell type') -> pd.DataFrame:
		"""Returns a DataFrame of the mean expression levels by tissue or cell type."""
		if gene_name not in self.df.index.get_level_values('Gene name'):
			raise ValueError("Gene with HGNC symbol {} not found.".format(gene_name))
		gene = self.df[self.df.index.get_level_values('Gene name') == gene_name]
		assert gene is not None
		return gene.groupby(group_by).mean().sort_values('Level', ascending=False)

	def tissue(self, name: str):
		return self.level(name, group_by='Tissue')

	def cell_type(self, name: str):
		return self.level(name, group_by='Cell type')

	def _load(self, path: Optional[PathLike] = None, filter_fn: Callable[[pd.DataFrame], pd.DataFrame]=pd.DataFrame.dropna) -> pd.DataFrame:
		"""
		Get a DataFrame of Human Protein Atlas tissue expression data, indexed by Gene name and with the 'Gene' and 'Reliability' columns dropped.
		The expression level ('Level') is replaced using this map: {'Not detected': 0, 'Low': 1, 'Medium': 2, 'High': 3}.
		Downloads the file from http://www.proteinatlas.org/download/normal_tissue.csv.zip and reloads from normal_tissue.csv.gz thereafter.
		"""
		Rezipper().dl_and_rezip(TissueTable.URL, path)
		tissue = pd.read_csv(path).drop('Gene', axis=1).drop('Reliability', axis=1)
		tissue = filter_fn(tissue)
		tissue['Level'] = tissue['Level'].map({'Not detected': 0, 'Low': 1, 'Medium': 2, 'High': 3}.get).astype(float)
		return tissue.set_index('Gene name')



__all__ = ['TissueTable']