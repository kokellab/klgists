# Originally from: https://gist.github.com/dmyersturnbull/66ee06f439affec38a452f2597efb087
# Douglas Myers-Turnbull wrote this for the Kokel Lab, which has released it under the Apache Software License, Version 2.0
# See the license file here: https://gist.github.com/dmyersturnbull/bfa1c3371e7449db553aaa1e7cd3cac1
# The list of copyright owners is unknown

import re
import warnings
import time

from chemspipy import ChemSpider

from typing import Iterable, Iterator, Optional, Tuple


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
                        if '@' not in result.smiles and '/' not in result.smiles and '\\' not in result.smiles
                    }
                    if len(no_sterocenters) == 1:
                        return next(iter(no_sterocenters))
                    elif len(no_sterocenters) > 1:
                        warnings.warn("There are somehow {} compounds with the same connectivity and no defined sterocenters for {}".format(len(no_sterocenters), name))
    
        return None  # give up

    def recover_spiders(self, names: Iterable[str], sleep_seconds: float=0.1) -> Iterator[Tuple[str, str]]:
        """Yields a SMILES string each time one is found. Returns a tuple of (name, smiles), which can be made into a dict."""
        for name in names:
            smiles = self.recover_spider(name)
            time.sleep(sleep_seconds)  # don't annoy the admins!
            if smiles is not None:
                yield name, smiles
