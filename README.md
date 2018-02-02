# Neko²

Built from the mistakes and learnings of Neko.

## Installation

```python
python3.6 -m pip install git+https://github.com/espeonageon/nekosquared
```

Run this in a `venv` for best results.

## Why don't you use `aiohttp` and `asyncpg`? They are faster!

This bot is designed to be as modular as possible. Each cog I design will
implement specific traits that are injected by using object orientation
design patterns. Unfortunately, Python does not support initialising objects
with async-marked `__init__` methods, and likewise, discord.py does not
support an asynchronous `__unload` function definition. It is therefore
messy and difficult to initialise objects that should be initialised from
an async context in a standard procedural method when it is a requirement
that the asynchronous operation be completed before proceeding. For this
reason, managing a set of threads in a pool for each trait that implements
blocking behaviour is easier. Unless the bot suddenly becomes used widely,
the performance impact of doing this is negligible. If the latter did
occur, I probably would be looking for somewhere else to host the script
rather than a Raspberry Pi 3 B with a wireless network connection to a
slow rural internet connection!

## Brought to you by...

This project uses multiple existing dependencies to make life a bit easier and
to reduce the amount of testing that has to take place. These dependencies
come from both PyPi and non-PyPi sources.

### From PyPi

- [aiofiles](https://pypi.python.org/pypi/aiofiles) - Asyncio file I/O wrapper.
- [cached_property](https://pypi.python.org/pypi/cached-property) - Cached
    property decorator implementations that also include thread-safe wrappers
    and cached properties that will revalidate after a given period of time.
- [psycopg2](https://pypi.python.org/pypi/psycopg2) - Python PostgreSQL adapter.
- [pyyaml](https://pypi.python.org/pypi/pyyaml) - YAML implementation.
- [requests](https://pypi.python.org/pypi/requests) - HTTP requests for humans.

### From elsewhere

- [Discord.py Rewrite](https://github.com/rapptz/discord.py/tree/rewrite) -
    The rewrite of the Discord.py API wrapper using asyncio.

## Looking for the old version?

Check it out [here](https://github.com/espeonageon/neko).
