"""
Holds callbacks for when we are about to shut the bot down. These can be
either futures or

Couldn't find another way of handling this sadly. Hooray for global variables.
"""
import asyncio
import functools


_calls = asyncio.Queue()


def on_shutdown(coro):
    _calls.put_nowait(coro)


async def terminate():
    while _calls.qsize():
        next_callable = await _calls.get()
        if asyncio.isfuture(next_callable):
            await next_callable
        elif isinstance(next_callable,
                        (functools.partial, functools.partialmethod)):
            next_callable()
        else:
            raise TypeError(f'Unexpected type {type(next_callable)!r} '
                            'Expected future, partial or partial method.')
