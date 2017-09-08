import re
import chemspipy
from chemspipy import ChemSpider
from typing import Iterable, Mapping, Optional, Iterator, Tuple
import warnings
import time


class ChemspiderSearcher:

    cs = None

    def __init__(self, api_key: str):
        self.cs = ChemSpider(api_key)

    def chemspider_names(self, names: Iterable[str], partial_dict: Mapping[str, chemspipy.objects.Compound]={}, sleep_secs_between:float=0.1) -> Mapping[str, chemspipy.objects.Compound]:
        """Build a dictionary mapping compound names to unique ChemSpider hits as chemspipy.objects.Compound objects, using partial_dict as a starting point.
        Does not modify partial_dict. Warns for each compound that has multiple or no hits.
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
            for result in self.cs.search(name): # blocks
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



# use your API key for fetching from ChemSpider
class SpiderRecovery:
    _cs = None
    _has_stero = re.compile('(?:\([RSrsEZez+\-]\))|(?:[RSrsEZez][- \(])')

    def __init__(self, chemspider_api_key: str):
        self._cs = ChemSpider(chemspider_api_key)

    def recover_spider(self, name: str) -> Optional[str]:
        """Makes a best-effort attempt to recover SMILES strings from compound names unambiguously by searching ChemSpider.
        Errs slightly on the side of failure.
        If the compound name doesn't contain R, S, E, or Z (case-insensitive) in parantheses or followed by a hyphen or space,
        assumes the compound has no defined sterocenters. In other words, it assumes minimal sterochemistry.
        Returns the SMILES string if it was found unambiguously; otherwise returns None.
        """

        results = self._cs.search(name)

        if len(results) == 1:
            return results[0].smiles

        elif len(results) > 0:  # try to recover if they're just enantiomers
            connectivities = {result.inchikey[0:14] for result in results}
            if len(connectivities) == 1:
                if self._has_stero.match(name) is None:
                    no_sterocenters = {result.smiles
                                       for result in results
                                       if
                                       '@' not in result.smiles and '/' not in result.smiles and '\\' not in result.smiles
                                       }
                    if len(no_sterocenters) == 1:
                        return next(iter(no_sterocenters))
                    elif len(no_sterocenters) > 1:
                        warnings.warn(
                            "There are somehow {} compounds with the same connectivity and no defined sterocenters for {}".format(
                                len(no_sterocenters), name))

        return None  # give up

    def recover_spiders(self, names: Iterable[str], sleep_seconds: float = 0.1) -> Iterator[Tuple[str, str]]:
        """Yields a SMILES string each time one is found. Returns a tuple of (name, smiles), which can be made into a dict."""
        for name in names:
            smiles = self.recover_spider(name)
            time.sleep(sleep_seconds)  # don't annoy the admins!
            if smiles is not None:
                yield name, smiles
