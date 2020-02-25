import logging
import json
import requests
import re
from datetime import datetime
from pathlib import Path
from typing import Iterator, Set, Union

logger = logging.getLogger('dscience_gists')


class Atc:
	def __init__(self, code: str, desc: str, parent):
		self.code = code
		self.desc = desc
		self.parent = parent
		self.level = len(code) if self.code != '/' else 0
		self.children = set()
	
	def __eq__(self, o):
		return isinstance(o, Atc) and self.code == o.code

	def __neq__(self, o):
		return self != o

	def __hash__(self):
		return hash(self.code)

	def __lt__(self, o):
		return isinstance(o, Atc) and self.code < o.code

	def __gt__(self, o):
		return isinstance(o, Atc) and self.code > o.code

	def __le__(self, o):
		return isinstance(o, Atc) and self.code <= o.code

	def __ge__(self, o):
		return isinstance(o, Atc) and self.code >= o.code
	
	def __repr__(self):
		return "→{:7} – {}".format(self.code, self.desc)

	def __str__(self): return repr(self)
	
	def is_root(self) -> bool:
		return self.parent is None
	
	def is_leaf(self) -> bool:
		if len(self.children) == 0 and self.level == 7:
			return True
		elif len(self.children) != 0 and self.level != 7:
			return False
		raise ValueError("Inconsistent leaf definition for {}".format(self))
	
	def ancestry(self) -> list:
		parents = []
		if self.parent is not None:
			for a in self.parent.ancestry():
				parents.append(a)
		parents.append(self)
		return parents
	
	def descendents(self):
		return {b for b in self.bfs() if b != self}
	
	def subtree(self):
		return AtcTree(self, {n.code: n for n in self.bfs()})
	
	def dfs(self):
		for node in self.children:
			yield from node.dfs()
			yield node
		yield self
	
	def bfs(self):
		yield self
		for node in self.children:
			yield node
			yield from node.dfs()
	
	def leaves(self):
		for node in self.bfs():
			if node.level == 7:
				yield node
	
	@classmethod
	def root(cls):
		return Atc('/', 'ROOT', None)


class AtcTree:
	def __init__(self, root: Atc, lookup: dict):
		self.root = root
		self._lookup = lookup
	
	def get(self) -> Atc:
		return self._lookup[Atc]
		
	def nodes(self) -> Set[Atc]:
		return set(self._lookup.values())
	
	def dfs(self) -> Iterator[Atc]:
		yield from self.root.dfs()
	
	def bfs(self) -> Iterator[Atc]:
		yield from self.root.bfs()
		
	def leaves(self) -> Iterator[Atc]:
		yield from self.root.leaves()
	
	def __len__(self):
		return len(self.nodes())
	
	def __repr__(self):
		return "AtcTree({} nodes @ {})".format(len(self._lookup), hex(id(self)))

	def __str__(self):
		return repr(self)


class AtcParser:
	
	URL = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/annotations/heading/JSON/?source=WHO%20ATC&heading=ATC+Code&response_type=save&response_basename=PubChemAnnotations_source=WHO%20ATC&heading=ATC+Code&page={page}'

	def __init__(self, cache_dir: Union[Path, str] = '.atc'):
		self.cache_dir = Path(cache_dir)
		self.cache_dir.mkdir(parents=True, exist_ok=True)

	def load(self, force_download: bool = False):
		atcs = {'/': Atc.root()}
		if not force_download and Path(self.cache_dir, 'is-done').exists():
			logger.debug("Loading ATC tree from cache...")
			self._load_from_cache(atcs)
		else:
			logger.info("Downloading ATC tree from pubchem.ncbi.nlm.nih.gov ...")
			self._download(atcs)
		logger.debug("Loaded {} ATC codes".format(len(atcs)))
		for atc in atcs.values():
			atc.children = sorted(list(atc.children))
		return AtcTree(atcs['/'], atcs)
	
	def _load_from_cache(self, atcs: dict):
		i = 1
		while True:
			p = self.cache_dir / 'page-{}.txt'.format(i)
			if p.exists():
				with open(p) as f:
					data = json.loads(f.read())['Annotations']['Annotation']
					for atc in self._parse(data, atcs):
						pass
				i += 1
	
	def _download(self, atcs: dict):
		response = requests.get(AtcParser.URL.format(page=1))
		data = response.json()['Annotations']
		n_pages = data['TotalPages']
		for i in range(1, n_pages+1):  # downloading page 1 twice, but whatever
			response = requests.get(AtcParser.URL.format(page=i))
			logger.debug("Downloading page {} of {}.".format(i, n_pages))
			(self.cache_dir / 'page-{}.txt'.format(i)).write_text(response.text)
			data = response.json()['Annotations']
			for atc in self._parse(data['Annotation'], atcs):
					pass
			(self.cache_dir / '.is_done').write_text(str(datetime.now()))
	
	def _parse(self, items: list, atcs: dict):
		pat = re.compile(r'^(?:<[^>]+>)? *([^ ]+) +- +(?:<[^>]+>)? *([^<]+).*$')
		root = atcs['/']
		for item in items:
			for v0 in [_['Value']['String'][0] for _ in item['Data'] if _['TOCHeading'] == 'ATC Code']:
				parent = root
				for v in v0.split('<br>'):
					m = pat.match(v.strip())
					code, name = m.group(1).strip(), m.group(2).strip()
					contains = code in atcs
					if code in atcs:
						child = atcs[code]
					else:
						child = Atc(code, name, parent)
					parent.children.add(child)
					parent = child
					if not contains:
						atcs[child.code] = child
						yield child
				# and it resets parent each loop
	
	def __repr__(self):
		return self.__name__

	def __str__(self): return repr(self)


__all__ = ['Atc', 'AtcTree', 'AtcParser']
