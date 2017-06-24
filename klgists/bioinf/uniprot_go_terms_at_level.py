# Requires https://gist.github.com/dmyersturnbull/efe32052bf4cf06df915

import os
import wget
import pandas as pd
from typing import Iterable, Union, Mapping, List
from goatools import obo_parser # uses https://github.com/tanghaibao/goatools
from goatools.obo_parser import GOTerm # NOT the same as FlatGoTerm, which has no knowledge of hierarchy


class GoTermsAtLevel:

	def __init__(self) -> None:
		self.obo = obo_parser.GODag('gene_ontology.1_2.obo')
		if not os.path.exists('gene_ontology.1_2.obo'):
			print("Downloading Gene Ontology OBO...")
			wget.download('http://www.geneontology.org/ontology/obo_format_1_2/gene_ontology.1_2.obo')
			self.obo = obo_parser.GODag('gene_ontology.1_2.obo')  # This will be used in query_obo_term
			print("Done downloading OBO.")


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
			if (term.has_parent):
				return [traverse_up(p, buildup_set, level) for p in term.parents]
			return None
		terms = set()
		traverse_up(self.query_obo_term(term_id), terms, level)
		return terms


	def go_term_ancestors_for_uniprot_id(self, uniprot_id: str, level: int, kinds_allowed: List[str] = ['P', 'F', 'C']) -> Iterable[GOTerm]:
		"""Gets the GO terms associated with a UniProt ID and returns a set of their ancestors at the specified level.
		The traversal is restricted to is-a relationships.
		Note that the level is the minimum number of steps to the root.
			Arguments:
				level: starting at 0 (root)
				kinds_allowed: a set containing any combination of 'P', 'F', or 'C'
		"""
		if len(kinds_allowed) == 0: return []
		terms = [term for term in self.go_terms_for_uniprot_id(uniprot_id) if term.kind in kinds_allowed]
		ancestor_terms = set()
		for term_id in [t.ID for t in terms]:
			ancestor_terms.update(self.get_ancestors_of_go_term(term_id, level))
		return ancestor_terms


	def go_term_ancestors_for_uniprot_id_as_df(self, uniprot_id: str, level: int, kinds_allowed: Iterable[str] = ['P', 'F', 'C']) -> pd.DataFrame:
		"""See go_term_ancestors_for_uniprot_id. Returns a Pandas DataFrame with columns IDand name."""
		df = pd.DataFrame(columns=['ID', 'name'])
		for term in self.go_term_ancestors_for_uniprot_id(uniprot_id, level, kinds_allowed):
			df.loc[len(df)] = pd.Series({'ID': term.id, 'name': term.name, 'level': term.level})
		return df.set_index('ID')


# Example: go_term_ancestors_for_uniprot_id_as_df('P42681', 2)