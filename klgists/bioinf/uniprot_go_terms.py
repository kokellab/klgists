# Requires https://gist.github.com/dmyersturnbull/c0717406eb46158401a9:
from silenced import silenced

import re
import uniprot # from https://github.com/boscoh/uniprot
import pandas as pd
import contextlib
import sys
from io import StringIO
from typing import Iterable, Union, Mapping

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


def fetch_uniprot_data(uniprot_ids: Union[str, Iterable[str]]) -> Iterable[Mapping[str, str]]:
    """Fetches a list of dicts of UniProt metadata, one per UniProt ID.
    Raises a ValueError if a UniProt ID wasn't found.
    """
    if isinstance(uniprot_ids, str): # not a list type
        uniprot_ids = [uniprot_ids]
    # if we don't prevent these here, we'll get a ValueError from below, which is confusing
    # That's because uniprot.fetch_uniprot_metadata will only return one per unique ID
    if len(set(uniprot_ids)) != len(uniprot_ids):
        raise ValueError('Set of UniProt IDs cannot contain duplicates')
    with silenced(stderr=False):
        uniprot_data = uniprot.fetch_uniprot_metadata(uniprot_ids)
    if uniprot_data is None or uniprot_data == {} or len(uniprot_data) != len(uniprot_ids):
        raise ValueError('At least one UniProt ID not found in {}'.format(str(uniprot_ids)))
    return list(uniprot_data.values())


def go_terms_for_uniprot_id(uniprot_id: str) -> Iterable[FlatGoTerm]:
    """Returns a list of FlatGoTerm objects from a UniProt ID."""
    term_strings = (fetch_uniprot_data(uniprot_id)[0])['go']
    return [FlatGoTerm(s) for s in term_strings]


def go_terms_for_uniprot_id_as_df(uniprot_id: str) -> pd.DataFrame:
    """Returns a Pandas DataFrame of GO terms from a UniProt ID."""
    df = pd.DataFrame(columns=['ID', 'kind', 'description', 'sourceId', 'sourceName'])
    for term in go_terms_for_uniprot_id(uniprot_id):
        df.loc[len(df)] = (term.to_series())
    return df.set_index('ID')


import pytest

def test_fetch_uniprot():
    """Tests some tricky edge cases of fetch_uniprot_data."""
    fetch_uniprot_data('P42681')
    fetch_uniprot_data(['P42681'])
    fetch_uniprot_data(['P42681', 'Q12851'])
    with pytest.raises(ValueError) as e:
        fetch_uniprot_data(['P42681', 'P42681']) # duplicates
    assert 'duplicates' in str(e.value).lower()
    with pytest.raises(ValueError):
        assert fetch_uniprot_data('')
    with pytest.raises(ValueError):
        assert fetch_uniprot_data('')


# Example: go_terms_for_uniprot_id('P42681')