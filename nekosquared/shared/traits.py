"""
Various thread and process pool templates.
"""
import asyncio
import concurrent.futures as futures
import logging
import os

import aiohttp
import aiofiles
import asyncpg

from nekosquared.engine import shutdown
from nekosquared.shared import config


__all__ = ('Scribe', 'CpuBoundPool', 'IoBoundPool', 'FsPool',
           'HttpPool', 'PostgresPool')


class _FakeCtx:
    def __init__(self, getter):
        self.__enter__ = lambda _: getter()
        self.__aenter__ = asyncio.coroutine(self.__enter__)
        self.__exit__ = lambda _: None
        self.__aexit__ = asyncio.coroutine(self.__exit__)


class Scribe:
    """Adds functionality to a class to allow it to log information."""
    logging.basicConfig(level='INFO')
    logger: logging.Logger

    def __init_subclass__(cls, **_):
        cls.logger: logging.Logger = logging.getLogger(type(cls).__name__)


def _magic_number(*, cpu_bound=False):
    """
    Returns the magic number for this machine. This is the number of
    concurrent execution media to spawn in a pool.
    :param cpu_bound: defaults to false. Determines if we are considering
        IO bound work (the default) or CPU bound.
    :return: 5 * the number of USABLE logical cores if we are IO bound. If we
        are CPU bound, we return 2 * the number of processor cores, as CPU
        bound work utilises the majority of it's allocated time to doing
        meaningful work, whereas IO is usually slow and consists of thread
        yielding. There is no point spamming the CPU with many more jobs than
        it can concurrently handle with CPU bound work, whereas it will provide
        a significant performance boost for IO bound work. We don't consider
        scheduler affinity for CPU bound as we expect that to use a process
        pool, which is modifiable by the kernel.
    """
    # OR with 1 to ensure at least 1 "node" is detected.
    if cpu_bound:
        return 2 * (os.cpu_count() or 1)
    else:
        return 5 * (len(os.sched_getaffinity(0)) or 1)


_processes, _threads = _magic_number(cpu_bound=True), _magic_number()
logging.getLogger('CpuBoundPool').info(
    f'Made pool for up to {_processes} cpu workers.')
logging.getLogger('IoBoundPool').info(
    f'Made pool for up to {_threads} thread workers.')

_cpu_pool = futures.ProcessPoolExecutor(_processes)
_io_pool = futures.ThreadPoolExecutor(_threads)
del _processes, _threads, _magic_number


@shutdown.on_shutdown
async def __on_shutdown():
    loop = asyncio.get_event_loop()
    await asyncio.gather(
        loop.call_soon_threadsafe(_cpu_pool.shutdown(True)),
        loop.call_soon_threadsafe(_io_pool.shutdown(True))
    )


class CpuBoundPool:
    """
    Trait that implements a process pool execution service for CPU-bound work.

    This is more costly to run than a thread, as it is essentially spawning a
    new process on the operating system each time we start one, however, these
    are cancellable. Generally this should only be used if work is very slow and
    consists mainly of CPU-based work.
    """
    @property
    def cpu_pool(self) -> futures.Executor:
        return _cpu_pool


class IoBoundPool:
    """
    Trait that implements a thread pool execution service for IO-bound work.

    This is less costly than a process pool, however, these are non-cancellable
    and are locked into the same affinity as the thread they are spawned by.
    There is also an issue of taking into account thread safety.
    """
    @property
    def io_pool(self) -> futures.Executor:
        return _io_pool


class FsPool(IoBoundPool, Scribe):
    """
    Trait that allows the acquisition of an asynchronous file handle from
    the local file system. This runs in the same pool of workers as the
    IoBoundPool uses.
    """
    @classmethod
    async def acquire_fp(cls, file, mode='r', buffering=-1, encoding=None,
                         errors=None, newline=None, closefd=True, opener=None):
        """Acquires an asynchronous file pointer to a file stream."""
        cls.logger.info(f'Opening {file!r} with mode {mode!r}')
        return await aiofiles.open(
            file, mode, buffering, encoding, errors, newline, closefd, opener,
            executor=_io_pool)


class HttpPool(Scribe):
    """
    Allows you to acquire an HTTP pool to use. This returns a context manager
    that can be used either in asynchronous or non asynchronous ``with`` blocks.
    """
    @classmethod
    async def acquire_http(cls) -> aiohttp.ClientSession:
        """
        :return: the client session.
        """
        if not hasattr(cls, '_http_pool'):
            cls.logger.info('Initialising HTTP pool.')
            cls._http_pool = aiohttp.ClientSession()

            @shutdown.on_shutdown
            async def shutdown_callback():
                cls.logger.info('Closing HTTP pool.')
                await cls._http_pool.close()
        else:
            cls.logger.info(f'Acquiring existing HTTP pool.')

        # noinspection PyTypeChecker
        return _FakeCtx(lambda: cls._http_pool).__enter__


class PostgresPool(Scribe):
    """
    Allows you to acquire a connection to the database from the connection pool.
    """
    @classmethod
    async def acquire_db(cls, timeout=None) -> asyncpg.Connection:
        """
        :param timeout: optional timeout.
        :return: connection.
        """

        if not hasattr(cls, f'__{cls.__name__}_postgres_pool'):
            cls.logger.info('Initialising PostgreSQL pool from config.')
            cfg = await config.get_config_data('database.yaml')
            cls.__postgres_pool = asyncpg.create_pool(**cfg)

            @shutdown.on_shutdown
            async def shutdown_callback():
                cls.logger.info('Closing PostgreSQL pool.')
                await cls.__postgres_pool.close()
        else:
            cls.logger.info(f'Acquiring existing PostgreSQL pool.')

        return await cls.__postgres_pool.acquire(timeout=timeout)


del _FakeCtx
