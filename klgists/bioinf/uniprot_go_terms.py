
import re
# from https://github.com/boscoh/uniprot
import uniprot
import pandas as pd
import os
import wget
from klgists.common.tools.sys_tools import IoTools
from goatools import obo_parser # uses https://github.com/tanghaibao/goatools
from goatools.obo_parser import GOTerm # NOT the same as FlatGoTerm, which has no knowledge of hierarchy

from typing import Iterable, Union, Mapping, List, Optional


go_pattern = re.compile('GO:(\d+); ([CFP]):([\dA-Za-z- ,\(\)]+); ([A-Z]+):([A-Za-z-_]+)\.')


class FlatGoTerm(object):
	"""A Gene Ontology term.
		Note:
			Not to be confused with GOTerm in goatools: obo_parser.GOTerm
		Attributes:
			ID (str); ex: GO:0005737
			kind (str: 'P'==process, 'C'==component, 'F'==function)
			description (str)
			sourceId (str); ex: IDA
			sourceName (str); ex: UniProtKB
	"""
	def __init_(self, ID: str, kind: str, description: str, sourceId: str, sourceName: str):
		self.ID = ID
		self.kind = kind
		self.description = description
		self.sourceId = sourceId
		self.sourceName = sourceName

	def __init__(self, string: str):
		"""Builds a GO term from a string from uniprot_obj['go'].
		Raises a ValueError if the syntax is wrong.
		"""
		match = go_pattern.search(string)
		if match is None:
			raise ValueError('String didn\'t match GO term pattern: {}'.format(string))
		self.ID = 'GO:' + match.group(1)
		self.kind = match.group(2)
		self.description = match.group(3)
		self.sourceId = match.group(4)
		self.sourceName = match.group(5)
	def to_series(self) -> pd.Series:
		return pd.Series(self.__dict__)


class UniProtGoTerms:

	def fetch_uniprot_data(self, uniprot_ids: Union[str, List[str]]) -> List[Mapping[str, str]]:
		"""Fetches a list of dicts of UniProt metadata, one per UniProt ID.
		Raises a ValueError if a UniProt ID wasn't found.
		"""
		if isinstance(uniprot_ids, str): # not a list type
			uniprot_ids = [uniprot_ids]
		# if we don't prevent these here, we'll get a ValueError from below, which is confusing
		# That's because uniprot.fetch_uniprot_metadata will only return one per unique ID
		if len(set(uniprot_ids)) != len(uniprot_ids):
			raise ValueError('Set of UniProt IDs cannot contain duplicates')
		with IoTools.silenced(no_stderr=False):
			uniprot_data = uniprot.fetch_uniprot_metadata(uniprot_ids)
		if uniprot_data is None or uniprot_data == {} or len(uniprot_data) != len(uniprot_ids):
			raise ValueError('At least one UniProt ID not found in {}'.format(str(uniprot_ids)))
		return list(uniprot_data.values())


	def go_terms_for_uniprot_id(self, uniprot_id: str) -> List[FlatGoTerm]:
		"""Returns a list of FlatGoTerm objects from a UniProt ID."""
		term_strings = (self.fetch_uniprot_data(uniprot_id)[0])['go']
		return [FlatGoTerm(s) for s in term_strings]


	def go_terms_for_uniprot_id_as_df(self, uniprot_id: str) -> pd.DataFrame:
		"""Returns a Pandas DataFrame of GO terms from a UniProt ID."""
		df = pd.DataFrame(columns=['ID', 'kind', 'description', 'sourceId', 'sourceName'])
		for term in self.go_terms_for_uniprot_id(uniprot_id):
			df.loc[len(df)] = (term.to_series())
		return df.set_index('ID')




class GoTermsAtLevel:
	"""
	Example: go_term_ancestors_for_uniprot_id_as_df('P42681', 2)
	"""
	def __init__(self) -> None:
		if os.path.exists('gene_ontology.1_2.obo'):
			self.obo = obo_parser.GODag('gene_ontology.1_2.obo')
		else:
			print("Downloading Gene Ontology OBO...")
			wget.download('http://www.geneontology.org/ontology/obo_format_1_2/gene_ontology.1_2.obo')
			self.obo = obo_parser.GODag('gene_ontology.1_2.obo')  # This will be used in query_obo_term
			print("Done downloading OBO.")
		self.substruct = UniProtGoTerms()


	def query_obo_term(self, term_id: str) -> GOTerm:
		"""Queries a term through the global obo.
		This function wraps the call to raise a ValueError if the term is not found;
		otherwise it only logs a warning.
		"""
		x = self.obo.query_term(term_id)
		if x is None:
			raise ValueError('Term ID {} not found'.format(x))
		return x


	def get_ancestors_of_go_term(self, term_id: str, level: int) -> Iterable[GOTerm]:
		"""
		From a GO term in the form 'GO:0007344', returns a set of ancestor GOTerm objects at the specified level.
		The traversal is restricted to is-a relationships.
		Note that the level is the minimum number of steps to the root.
			Arguments:
				level: starting at 0 (root)
		"""
		def traverse_up(term, buildup_set, level):
			if term.level == level:
				buildup_set.add(term)
			if term.has_parent:
				return [traverse_up(p, buildup_set, level) for p in term.parents]
			return None
		terms = set()
		traverse_up(self.query_obo_term(term_id), terms, level)
		return terms


	def go_term_ancestors_for_uniprot_id(self, uniprot_id: str, level: int, kinds_allowed: Optional[List[str]] = None) -> Iterable[GOTerm]:
		"""Gets the GO terms associated with a UniProt ID and returns a set of their ancestors at the specified level.
		The traversal is restricted to is-a relationships.
		Note that the level is the minimum number of steps to the root.
			Arguments:
				level: starting at 0 (root)
				kinds_allowed: a set containing any combination of 'P', 'F', or 'C'
		"""
		if kinds_allowed is None: kinds_allowed =  ['P', 'F', 'C']
		if len(kinds_allowed) == 0: return []
		terms = [term for term in self.substruct.go_terms_for_uniprot_id(uniprot_id) if term.kind in kinds_allowed]
		ancestor_terms = set()
		for term_id in [t.ID for t in terms]:
			ancestor_terms.update(self.get_ancestors_of_go_term(term_id, level))
		return ancestor_terms


	def go_term_ancestors_for_uniprot_id_as_df(self, uniprot_id: str, level: int, kinds_allowed: Optional[List[str]] = None) -> pd.DataFrame:
		if kinds_allowed is None: kinds_allowed =  ['P', 'F', 'C']
		"""See go_term_ancestors_for_uniprot_id. Returns a Pandas DataFrame with columns IDand name."""
		df = pd.DataFrame(columns=['ID', 'name'])
		for term in self.go_term_ancestors_for_uniprot_id(uniprot_id, level, kinds_allowed):
			df.loc[len(df)] = pd.Series({'ID': term.id, 'name': term.name, 'level': term.level})
		return df.set_index('ID')


__all__ = ['FlatGoTerm', 'UniProtGoTerms', 'GoTermsAtLevel']
