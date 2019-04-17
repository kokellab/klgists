"""
A collection of decorators.
"""

from typing import Optional, Callable, Set
import signal
from functools import wraps
from abc import abstractmethod, ABC, ABCMeta
from functools import total_ordering
from dataclasses import dataclass
from overrides import overrides
from deprecated import deprecated

from klgists.common import decorator


class SpecialStr(str):
	"""
	A string that can be displayed with Jupyter with line breaks and tabs.
	"""
	def __init__(self, s: str):
		super().__init__()
		self.s = str(s)
	def __repr__(self): return repr(self.s)
	def __str__(self): return str(self.s)
	def _repr_html_(self):
		return str(self.s.replace('\n', '<br />').replace('\t', '&emsp;&emsp;&emsp;&emsp;'))


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
		return str(built)


def _var_items(obj, only, exclude):
	return [
		(key, value)
		for key, value in vars(obj).items()
		if (only is None) or (key in only)
		if not exclude(key)
	]

def _var_values(obj, only, exclude):
	items = vars(obj).items()
	return [value for key, value in items if ((only is None) or key in only) and not exclude(key) and value is not None]

def _auto_hash(self, only: Optional[Set[str]], exclude: Optional[Callable[[str], bool]]):
	if exclude is None: exclude = lambda _: False
	return hash(tuple(_var_values(self, only, exclude)))

def _auto_eq(self, other, only: Optional[Set[str]], exclude: Optional[Callable[[str], bool]]):
	if type(self) != type(other):
		raise TypeError("Type {} is not the same as type {}".format(type(self), type(other)))
	if exclude is None: exclude = lambda _: False
	return _var_values(self, only=only, exclude=exclude) == _var_values(other, only, exclude)


@decorator
def auto_eq(only: Optional[Set[str]] = None, exclude: Optional[Callable[[str], bool]] = None):
	"""
	Decorator.
	Auto-adds a __hash__ function by hashing its attributes.
	:param only: Only include these attributes
	:param exclude: Exclude these attributes
	"""
	def dec(cls):
		def __eq(self, other):
			return _auto_eq(self, other, only, exclude)
		cls.__eq__ = __eq
		return cls
	return dec


@decorator
def auto_hash(only: Optional[Set[str]] = None, exclude: Optional[Callable[[str], bool]] = None):
	"""
	Decorator.
	Auto-adds a __hash__ function by hashing its attributes.
	:param only: Only include these attributes
	:param exclude: Exclude these attributes
	"""
	def dec(cls):
		def __hash(self):
			return _auto_hash(self, only, exclude)
		cls.__hash__ = __hash
		return cls
	return dec


def _gen_str(
		self,
		only: Optional[Set[str]] = None,
		exclude: Optional[Callable[[str], bool]] = None,
		bold_surround: Callable[[str], str] = str, em_surround: Callable[[str], str] = str,
		delim: str = ', ', eq: str = '=', opening: str = '(', closing: str = ')',
		with_address: bool = True
):
	if exclude is None: exclude = lambda _: False
	_vars = _var_items(self, only, exclude)
	return (
		bold_surround(self.__class__.__name__) +
		opening +
		delim.join([k + eq + str(v) for k, v in _vars]) +
		em_surround(' @ ' + str(hex(id(self))) if with_address else '') +
		closing
	)

@decorator
def auto_repr(
		only: Optional[Set[str]] = None, exclude: Optional[Callable[[str], bool]] = lambda a: False
):
	def dec(cls):
		def __repr(self):
			return _gen_str(self, only=only, exclude=exclude, with_address=True)
		cls.__repr__ = __repr
		return cls
	return dec


@decorator
def auto_str(
		only: Optional[Set[str]] = None,
		exclude: Optional[Callable[[str], bool]] = lambda a: a.startswith('_'),
		with_address: bool = False
):
	def dec(cls):
		def __str(self):
			return _gen_str(self, only=only, exclude=exclude, with_address=with_address)
		cls.__str__ = __str
		return cls
	return dec


@decorator
def auto_html(
		only: Optional[Set[str]] = None,
		exclude: Optional[Callable[[str], bool]] = lambda a: lambda b: b.startswith('_'),
		with_address: bool = True
):
	def dec(cls):
		def __html(self):
			return SpecialStr(_gen_str(self, only=only, exclude=exclude, with_address=with_address, bold_surround = lambda c: '<strong>' + c + '</strong>', em_surround = lambda c: '<em>' + c + '</em>'))
		cls._repr_html = __html
		return cls
	return dec


@decorator
def auto_repr_str(
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
	"""
	def dec(cls):
		def __str(self):
			return _gen_str(self, only=None, exclude=exclude_simple, with_address=False)
		def __html(self):
			return SpecialStr(_gen_str(self, only=None, exclude=exclude_html, with_address=True, bold_surround = lambda c: '<strong>' + c + '</strong>', em_surround = lambda c: '<em>' + c + '</em>'))
		def __repr(self):
			return _gen_str(self, only=None, exclude=exclude_all, with_address=True)
		cls.__str__ = __str
		cls.__repr__ = __repr
		cls._repr_html_ = __html
		return cls
	return dec


@decorator
def auto_info(only: Optional[Set[str]] = None, exclude: Optional[Callable[[str], bool]] = lambda a: a.startswith('_')):
	"""
	Decorator.
	Auto-adds a function 'info' that outputs a pretty multi-line representation of the instance and its attributes.
	:param only:
	:param exclude:
	"""
	def dec(cls):
		def __info(self):
			return _InfoSpecialStr(_gen_str(self, delim='\n\t', eq=' = ', opening='(\n\t', closing='\n)', with_address=False, only=only, exclude=exclude))
		cls.info = __info
		return cls
	return dec


@decorator
def auto_obj():
	"""
	Auto-adds __eq__, __hash__, __repr__, __str__, and _repr_html_.
	See the decorators for auto_eq, auto_hash, and auto_repr for more details.
	"""
	def __str(self):
		return _gen_str(self, exclude=lambda a: a.startswith('_'), with_address=False)
	def __html(self):
		return SpecialStr(_gen_str(self, only=None, exclude=lambda a: a.startswith('_'), with_address=True, bold_surround = lambda c: '<strong>' + c + '</strong>'))
	def __repr(self):
		return _gen_str(self, exclude=lambda _: False, with_address=True)
	def __hash(self):
		return _auto_hash(self, only=None, exclude=None)
	def __eq(self):
		return _auto_eq(self, None, only=None, exclude=None)
	def dec(cls):
		cls.__eq__ = __eq
		cls.__str__ = __str
		cls.__repr__ = __repr
		cls.__hash__ = __hash
		cls._repr_html_ = __html
		return cls
	return dec


@decorator
def float_type(attribute: str):
	"""
	Decorator.
	Auto-adds a __float__ using the __float__ of some attribute.
	Used to annotate a class as being "essentially an float".
	:param attribute: The name of the attribute of this class
	"""
	def dec(cls):
		cls.__float__ = lambda: float(getattr(cls, attribute))
		return cls
	return dec

@decorator
def int_type(attribute: str):
	"""
	Decorator.
	Auto-adds an __int__ using the __int__ of some attribute.
	Used to annotate a class as being "essentially an integer".
	:param attribute: The name of the attribute of this class
	"""
	def dec(cls):
		cls.__float__ = lambda: float(getattr(cls, attribute))
		return cls
	return dec


@decorator
def iterable_over(attribute: str):
	"""
	Decorator.
	Auto-adds an __iter__ over elements in an iterable attribute.
	Used to annotate a class as being "essentially an iterable" over some elements.
	:param attribute: The name of the attribute of this class
	"""
	def dec(cls):
		cls.__iter__ = lambda: iter(getattr(cls, attribute))
		return cls
	return dec


@decorator
def collection_over(attribute: str):
	"""
	Decorator.
	Auto-adds an __iter__ and __len__ over elements in a collection attribute.
	Used to annotate a class as being "essentially a collection" over some elements.
	:param attribute: The name of the attribute of this class
	"""
	def dec(cls):
		cls.__iter__ = lambda: iter(getattr(cls, attribute))
		cls.__len__ = lambda: len(getattr(cls, attribute))
		return cls
	return dec



@decorator
def sequence_over(attribute: str):
	"""
	Decorator.
	Auto-adds __getitem__ and __len__ over elements in an iterable attribute.
	Used to annotate a class as being "essentially a list" over some elements.
	:param attribute: The name of the attribute of this class
	"""
	def dec(cls):
		cls.__getitem__ = lambda e: getattr(cls, attribute)[e]
		cls.__len__ = lambda: len(getattr(cls, attribute))
		return cls
	return dec

@decorator
def auto_singleton(cls):
	"""
	Makes it so the constructor returns a singleton instance.
	The constructor CANNOT take arguments.
	Example usage:
	>>> @auto_singleton
	>>> class MyClass: pass
	>>> mysingleton = MyClass()
	"""
	instances = {}
	def get_instance():
		if cls not in instances:
			instances[cls] = cls()
		return instances[cls]
	return get_instance


@decorator
def auto_timeout(seconds: int):
	def dec(func):
		def _handle_timeout(the_signal, the_frame):
			raise TimeoutError("The call timed out")
		def my_fn(*args, **kwargs):
			signal.signal(signal.SIGALRM, _handle_timeout)
			signal.alarm(seconds)
			try:
				result = func(*args, **kwargs)
			finally:
				signal.alarm(0)
			return result
		return wraps(func)(my_fn)
	return dec


@decorator
def override_recommended(cls):
	"""
	Decorator.
	Overriding this class is generally recommended (but not required).
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
	"""
	return cls

@decorator
def external(cls):
	"""
	Decorator.
	This class or package is meant to be used *only* by code outside this project.
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
	"""
	return cls

@decorator
def thread_safe(cls):
	return cls

@decorator
def not_thread_safe(cls):
	return cls

@decorator
def builder(cls):
	"""
	Decorator.
	This class implements a builder pattern.
	"""
	return cls

@decorator
def tools(cls):
	"""
	Decorator.
	This class only defines static utility functions.
	"""
	return cls

@decorator
def cache(cls):
	"""
	Decorator.
	This class implements some kind of cache.
	"""
	return cls

@decorator
def caching(cls):
	"""
	Decorator.
	Instances of this class cache objects.
	"""
	return cls

@decorator
def final(cls):
	"""
	Decorator.
	This class should not be inherited from.
	"""
	return cls


__all__ = [
	'decorator',
	'dataclass',
	'auto_repr_str', 'auto_str', 'auto_repr', 'auto_html', 'auto_info',
	'auto_eq', 'auto_hash', 'total_ordering',
	'auto_timeout',
	'iterable_over', 'collection_over', 'sequence_over',
	'float_type', 'int_type',
	'auto_timeout',
	'abstractmethod', 'ABC', 'ABCMeta',
	'override_recommended', 'overrides',
	'deprecated', 'final', 'might_change',
	'internal', 'external', 'reserved',
	'thread_safe', 'not_thread_safe',
	'singleton', 'builder', 'tools', 'cache', 'caching'
]
