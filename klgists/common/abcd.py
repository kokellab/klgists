"""
A collection of decorators.
"""

from warnings import warn
from typing import Optional, Any, Callable
from abc import abstractmethod, ABC, ABCMeta
try:
	from dataclasses import dataclass
except ImportError:
	warn("Could not import dataclass: Are you using Python 3.7+?")
	dataclass = None

from overrides import overrides
from deprecated import deprecated

from klgists.common import decorator



#############
# TODO The arguments to these decorators don't work
#############


class SpecialStr:
	"""
	A string that can be displayed with Jupyter with line breaks and tabs.
	"""
	def __init__(self, s: str):
		self.s = s
	def __repr__(self): return repr(self.s)
	def __str__(self): return str(self.s)
	def _repr_html_(self):
		return self.s.replace('\n', '<br />').replace('\t', '&emsp;&emsp;&emsp;&emsp;')


class _InfoSpecialStr(SpecialStr):
	def _repr_html_(self):
		if len(self.s) == 0: return self.s
		lines = self.s.split('\n')
		built = '<strong>' + lines[0] + '</strong><br/>\n'
		if len(lines) > 1:
			for line in lines[1:-1]:
				if '=' in line:
					k, v = line[:line.index('=')], line[line.index('='):]
					built += '&emsp;&emsp;&emsp;&emsp;<strong>' + k + '</strong>' + v + '<br/>\n'
				else:
					built += line + '<br />\n'
		built += '<strong>)</strong>\n'
		return built


@deprecated
@decorator
def auto_comparator(cls, with_equality: bool = False):
	"""
	Decorator. DEPRECATED. Use klgists.core.abcd instead.
	On a class that has __lt__ defined, auto-adds __le__, __get__, __le__, and optionally __eq__ and __ne__.
	__le__, __get__, and __le__ will be defined in the obvious way using __lt__.
	__eq__ will be defined as not __lt__ and not __gt__, and __ne__ as not __eq__.
	:param cls: The class
	:param with_equality: Also add __eq__ and __ne__
	:return: The class back
	"""
	def __eq(self, other):
		return not self < other and not other < self
	def __ne(self, other):
		return self < other or other < self
	def __gt(self, other):
		return other < self
	def __ge(self, other):
		return not self < other
	def __le(self, other):
		return not other < self
	cls.__gt__ = __gt
	cls.__ge__ = __ge
	cls.__le__ = __le
	if with_equality:
		cls.__eq__ = __eq
		cls.__ne__ = __ne

def _var_items(obj, exclude):
	return [
		(key, value)
		for key, value in vars(obj).items()
		if not exclude(key)
	]

def _var_values(obj, exclude):
	items = vars(obj).items()
	return [value for key, value in items if not exclude(key) and value is not None]

def _auto_hash(self, exclude: Optional[Callable[[str], bool]] = None):
	if exclude is None: exclude = lambda _: False
	return hash(_var_values(self, exclude))

def _auto_eq(self, other, exclude: Optional[Callable[[str], bool]] = None):
	if type(self) != type(other):
		raise TypeError("Type {} is not the same as type {}".format(type(self), type(other)))
	if exclude is None: exclude = lambda _: False
	if exclude is None: exclude = {}
	return _var_values(self, exclude) == _var_values(other, exclude)


@decorator
def auto_eq(cls, exclude: Optional[Callable[[str], bool]] = None):
	"""
	Decorator.
	Auto-adds a __hash__ function by hashing its attributes.
	:param cls: The class
	:param exclude: Exclude these attributes
	:return: The same class
	"""
	def __eq(self):
		return _auto_eq(self, exclude)
	cls.__eq__ = __eq
	return cls


@decorator
def auto_hash(cls, exclude: Optional[Callable[[str], bool]] = None):
	"""
	Decorator.
	Auto-adds a __hash__ function by hashing its attributes.
	:param cls: The class
	:param exclude: Exclude these attributes
	:return: The same class
	"""
	def __hash(self):
		return _auto_hash(self, exclude)
	cls.__hash__ = __hash
	return cls


def _gen_str(
		self,
		exclude: Optional[Callable[[str], bool]] = None,
		bold_surround: Callable[[str], str] = str, em_surround: Callable[[str], str] = str,
		delim: str = ', ', eq: str = '=', opening: str = '(', closing: str = ')',
		with_address: bool = True
):
	if exclude is None: exclude = lambda _: False
	_vars = _var_items(self, exclude)
	return (
		bold_surround(self.__class__.__name__) +
		opening +
		delim.join([k + eq + str(v) for k, v in _vars]) +
		em_surround(' @ ' + str(hex(id(self))) if with_address else '') +
		closing
	)

@decorator
def auto_repr(
		cls,
		exclude: Optional[Callable[[str], bool]] = lambda a: False
):
	def __repr(self):
		return _gen_str(self, exclude=exclude, with_address=True)
	cls.__repr__ = __repr
	return cls

@decorator
def auto_str(
		cls,
		exclude: Optional[Callable[[str], bool]] = lambda a: a.startswith('_'),
		with_address: bool = False
):
	def __str(self):
		return _gen_str(self, exclude=exclude, with_address=with_address)
	cls.__str__ = __str
	return cls

@decorator
def auto_html(
		cls,
		exclude: Optional[Callable[[str], bool]] = lambda a: lambda b: b.startswith('_'),
		with_address: bool = True
):
	def __html(self):
		return SpecialStr(_gen_str(self, exclude=exclude, with_address=with_address, bold_surround = lambda c: '<strong>' + c + '</strong>', em_surround = lambda c: '<em>' + c + '</em>'))
	cls._repr_html = __html
	return cls

@decorator
def auto_repr_str(
		cls,
		exclude_simple: Optional[Callable[[str], bool]] = lambda a: a.startswith('_'),
		exclude_html: Optional[Callable[[str], bool]] = lambda a: a.startswith('_'),
		exclude_all: Optional[Callable[[str], bool]] = lambda a: False
):
	"""
	Decorator.
	Auto-adds __repr__, __str__, and __md that show the attributes:
		- __str__ will include attributes in neither exclude_all nor exclude_simple
		- _repr_html_ will include attributes in neither exclude_all nor exclude_simple and will show the hexadecimal address
		- __repr__ will include attributes not in exclude_all and will show the hexadecimal address
	The _repr_html_ will be used by Jupyter display.
	Examples:
		repr(point) == Point(angle=0.3, radius=4, _style='point' @ 0x5528ca3)
		str(point) == Point(angle=0.3, radius=4)
		_repr_html_(point) == Point(angle=0.3, radius=4 @ 0x5528ca3)
	:param exclude_html: Exclude for _repr_html
	:param exclude_simple: Exclude attributes matching these names in human-readable strings (str and _repr_html)
	:param exclude_all: Exclude these attributes in all the functions
	:param cls: The class
	:return: The same class
	"""
	def __str(self):
		return _gen_str(self, exclude=exclude_simple, with_address=False)
	def __html(self):
		return SpecialStr(_gen_str(self, exclude=exclude_html, with_address=True, bold_surround = lambda c: '<strong>' + c + '</strong>', em_surround = lambda c: '<em>' + c + '</em>'))
	def __repr(self):
		return _gen_str(self, exclude=exclude_all, with_address=True)
	cls.__str__ = __str
	cls.__repr__ = __repr
	cls._repr_html_ = __html
	return cls

@decorator
def auto_info(cls, exclude: Optional[Callable[[str], bool]] = lambda a: a.startswith('_')):
	"""
	Decorator.
	Auto-adds a function 'info' that outputs a pretty multi-line representation of the instance and its attributes.
	:param exclude:
	:param cls: The class
	:return: The same class
	"""
	def __info(self):
		return _InfoSpecialStr(_gen_str(self, delim='\n\t', eq=' = ', opening='(\n\t', closing='\n)', with_address=False, exclude=exclude))
	cls.info = __info
	return cls


@decorator
def auto_obj(cls):
	"""
	Auto-adds __eq__, __hash__, __repr__, __str__, and _repr_html_.
	See the decorators for auto_eq, auto_hash, and auto_repr for more details.
	:param cls: The class
	:return: The same class with added methods
	"""
	def __str(self):
		return _gen_str(self, exclude=lambda a: a.startswith('_'), with_address=False)
	def __html(self):
		return SpecialStr(_gen_str(self, exclude=lambda a: a.startswith('_'), with_address=True, bold_surround = lambda c: '<strong>' + c + '</strong>'))
	def __repr(self):
		return _gen_str(self, exclude=lambda _: False, with_address=True)
	def __hash(self):
		return _auto_hash(self, None)
	def __eq(self):
		return _auto_eq(self, None)
	cls.__eq__ = __eq
	cls.__str__ = __str
	cls.__repr__ = __repr
	cls.__hash__ = __hash
	cls._repr_html_ = __html
	return cls


@decorator
def override_recommended(cls):
	"""
	Decorator.
	Overriding this class is generally recommended (but not required).
	:param cls: The class
	:return: The same class
	"""
	return cls

@decorator
def might_change(cls):
	return cls

@decorator
def internal(cls):
	"""
	Decorator.
	This class or package is meant to be used only by code within this project.
	:param cls: The class
	:return: The same class
	"""
	return cls

@decorator
def external(cls):
	"""
	Decorator.
	This class or package is meant to be used *only* by code outside this project.
	:param cls: The class
	:return: The same class
	"""
	return cls

@decorator
def singleton(cls):
	return cls

@decorator
def reserved(cls):
	"""
	Decorator.
	This package, class, or function is empty but is declared for future use.
	:param cls: The class
	:return: The same class
	"""
	return cls

@decorator
def thread_safe(cls):
	return cls

@decorator
def not_thread_safe(cls):
	return cls

@decorator
def builder(cls, builds: Optional[Any] = None):
	"""
	Decorator.
	This class implements a builder pattern.
	:param cls: The class
	:param builds: The class this builder creates
	:return: The same class
	"""
	return cls

@decorator
def tools(cls):
	"""
	Decorator.
	This class only defines static utility functions.
	:param cls: The class
	:return: The same class
	"""
	return cls

@decorator
def cache(cls):
	"""
	Decorator.
	This class implements some kind of cache.
	:param cls: The class
	:return: The same class
	"""
	return cls

@decorator
def caching(cls):
	"""
	Decorator.
	Instances of this class cache objects.
	:param cls: The class
	:return: The same class
	"""
	return cls

@decorator
def final(cls):
	"""
	Decorator.
	This class should not be inherited from.
	:param cls: The class
	:return: The same class
	"""
	return cls


__all__ = [
	'decorator',
	'dataclass',
	'auto_repr_str', 'auto_str', 'auto_repr', 'auto_html', 'auto_info',
	'auto_eq', 'auto_hash', 'auto_comparator',
	'abstractmethod', 'ABC', 'ABCMeta',
	'override_recommended', 'overrides',
	'deprecated', 'final', 'might_change',
	'internal', 'external', 'reserved',
	'thread_safe', 'not_thread_safe',
	'singleton', 'builder', 'tools', 'cache', 'caching'
]
