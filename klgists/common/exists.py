# coding=utf-8

from typing import Callable, TypeVar, Iterable
T = TypeVar('T')

def exists(keep_predicate: Callable[[T], bool], seq: Iterable[T]) -> bool:
    """Efficient existential quantifier for a filter() predicate.
    Returns true iff keep_predicate is true for one or more elements."""
    for e in seq:
        if keep_predicate(e): return True  # short-circuit
    return False
