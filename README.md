# Neko²

Built from the mistakes and learnings of Neko.

## Installation

```python
python3.6 -m pip install git+https://github.com/espeonageon/nekosquared
```

Run this in a `venv` for best results.

## The config files

This bot looks in the current working directory for a directory called `config`.
It will look in here for any configuration files that are needed. These
configuration files may be in INI, JSON or YAML format, depending on the most
appropriate implementation. Example config files can be found in the `ex-config`
directory of this repository.

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
