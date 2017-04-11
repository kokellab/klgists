# Douglas Myers-Turnbull wrote this while at UCSF. Because of this, the list of copyright owners is unknown and is not licensed (sorry!).

import chemspipy
from chemspipy import ChemSpider
import warnings
from typing import Iterable, Mapping, Optional
import warnings
import time

# use your API key for fetching from ChemSpider
cs = ChemSpider('TO-DO')

def chemspider_names(names: Iterable[str], partial_dict: Mapping[str, chemspipy.objects.Compound]={}, sleep_secs_between:float=0.1) -> Mapping[str, chemspipy.objects.Compound]:
    """Build a dictionary mapping compound names to unique ChemSpider hits as chemspipy.objects.Compound objects, using partial_dict as a starting point.
    Does not modify partial_dict. Warns for each compound that has multiple or no hits.
    REQUIRED GLOBAL: A ChemSpider instance named cs.
    Immediately pickling the fetched results may be a good idea.
    Example usage:
        for compounds in chemspider_names(['Trichostatin A', 'Oxamflatin', 'Vinblastine']):
            print("{} → {}".format(result.csid, result.smiles))
    Result:
        UserWarning: Multiple (2) hits found for Oxamflatin
        392575 → C[C@H](/C=C(\C)/C=C/C(=O)NO)C(=O)c1ccc(cc1)N(C)C
        12773 → CC[C@@]1(C[C@H]2C[C@@](c3c(c4ccccc4[nH]3)CCN(C2)C1)(c5cc6c(cc5OC)N([C@@H]7[C@]68CCN9[C@H]8[C@@](C=CC9)([C@H]([C@@]7(C(=O)OC)O)OC(=O)C)CC)C)C(=O)OC)O
    """
    def fetch(name: str) -> Optional[chemspipy.objects.Compound]:
        results = []
        for result in cs.search(name): # blocks
            results.append(result)
        if len(results) == 0:
            warnings.warn("No results found for {}".format(name))
        elif len(results) > 1:
            warnings.warn('Multiple ({}) hits found for {}'.format(len(results), name))
        else:
            return results[0]

    new_dict = partial_dict.copy()
    for name in set(names) - set(new_dict.keys()):
        got = fetch(name)
        time.sleep(sleep_secs_between)
        if got is not None:
            new_dict[name] = got
    return new_dict

