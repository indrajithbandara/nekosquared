"""
Algorithm stuff.
"""


def find(predicate, iterable):
    """
    Attempts to find the first match for the given predicate in the iterable.

    If the element is not found, then ``None`` is returned.
    """
    for el in iterable:
        if predicate(el):
            return el


async def find_async(async_predicate, iterable):
    """
    See ``find``. This operates in the same way, except we await the
    predicate on each call.
    """
    for el in iterable:
        if await async_predicate(el):
            return el


async def find_async_iterator(async_predicate, async_iterator):
    """
    Same as ``find_async``, but treats the iterator as an ``await``able
    object.
    """
    for el in await async_iterator:
        if await async_predicate(el):
            return el


def find_all(predicate, iterable):
    """
    Yields all matches for the predicate across the iterable.
    """
    for el in iterable:
        if predicate(el):
            yield el