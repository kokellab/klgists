
from typing import Iterator, Dict, List, ItemsView, KeysView, ValuesView

from klgists.common.exceptions import MissingConfigEntry


class TomlData:
	"""A better TOML data structure than a plain dict.
	Usage examples:
		data = TomlData({'x': {'y': {'z': 155}}})
		print(data['x.y.z'])   # prints 155
		data.sub('x.y')        # returns a new TomlData for {'z': 155}
		data.nested_keys()     # returns all keys and sub-keys
	"""
	def __init__(self, top_level_item: Dict[str, object]):
		assert top_level_item is not None
		self.top = top_level_item

	def __str__(self) -> str:
		return repr(self)
	def __repr__(self) -> str:
		return "TomlData({})".format(str(self.top))

	def __getitem__(self, key: str) -> Dict[str, object]:
		return self.sub(key).top

	def get_str(self, key: str) -> str:
		return str(self.__as(key, str))

	def get_int(self, key: str) -> int:
		# noinspection PyTypeChecker
		return int(self.__as(key, int))

	def get_bool(self, key: str) -> int:
		# noinspection PyTypeChecker
		return bool(self.__as(key, bool))

	def get_str_list(self, key: str) -> List[str]:
		return self.__as_list(key, str)

	def get_int_list(self, key: str) -> List[int]:
		return self.__as_list(key, int)

	def get_float_list(self, key: str) -> List[int]:
		return self.__as_list(key, int)

	def get_bool_list(self, key: str) -> List[int]:
		return self.__as_list(key, bool)

	def get_float(self, key: str) -> int:
		# noinspection PyTypeChecker
		return int(self.__as(key, float))

	def __as_list(self, key: str, clazz):
		def to(v):
			if not isinstance(v, clazz):
				raise TypeError("{}={} is a {}, not {}".format(key, v, type(v), clazz))
			return [to(v) for v in self[key]]

	def __as(self, key: str, clazz):
		v = self[key]
		if isinstance(v, clazz):
			return v
		else:
			raise TypeError("{}={} is a {}, not {}".format(key, v, type(v), clazz))

	def sub(self, key: str):
		"""Returns a new TomlData with its top set to items[1][2]..."""
		items = key.split('.')
		item = self.top
		for i, s in enumerate(items):
			if s not in item: raise MissingConfigEntry(
				"{} is not in the TOML; failed at {}"
				.format(key, '.'.join(items[:i+1]))
			)
			item = item[s]
		return TomlData(item)

	def items(self) -> ItemsView[str, object]:
		return self.top.items()

	def keys(self) -> KeysView[str]:
		return self.top.keys()

	def values(self) -> ValuesView[object]:
		return self.top.values()

	def nested_keys(self, separator='.') -> Iterator[str]:
		for lst in self.nested_key_lists(self.top):
			yield separator.join(lst)

	def nested_key_lists(self, dictionary: Dict[str, object], prefix=None) -> Iterator[List[str]]:
		prefix = prefix[:] if prefix else []
		if isinstance(dictionary, dict):
			for key, value in dictionary.items():
				if isinstance(value, dict):
					for result in self.nested_key_lists(value, [key] + prefix): yield result
				else: yield prefix + [key]
		else: yield dictionary


__all__ = ['TomlData']
