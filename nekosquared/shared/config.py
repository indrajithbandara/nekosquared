"""
Handles reading config files.
"""
import asyncio
import io
import os

import aiofiles


CONFIG_DIRECTORY = 'config'


class ConfigFile:
    """
    Representation of a configuration file that allows for read-only
    access. This model assumes that the config file is not changeable at
    runtime; thus the data is cached after the first access.

    Note. This is not thread-safe.

    The constructor will block for a very short period of time whilst it
    checks that the file is a valid file inode and that it exists. This is only
    really a problem if you are constantly making these objects in a coroutine
    and you have a very slow file system.

    The call operator

    :param path: the path of the file to read.
    :param deserializer: the ``load`` method for the deserializer to use.
            If unspecified, we try to autodetect the serializer to use.
            The deserializer must accept one argument and this must be a file
            pointer to read from. Currently supported serializers for
            auto-detection are ``.json``, ``.yaml`` and ``.ini``.
    """
    def __init__(self, path, *, deserializer=None):
        if deserializer is None:
            if path.endswith('.json'):
                import json
                deserializer = json.load
            elif path.endswith('.yaml'):
                import yaml
                deserializer = yaml.load
            elif path.endswith('.ini'):
                from nekosquared.shared import ini
                deserializer = ini.load
            else:
                raise ModuleNotFoundError('Could not detect deserializer to '
                                          f'use for {path}')

        if not os.path.exists(path):
            raise FileNotFoundError(f'{path!r} does not exist.')
        elif not os.path.isfile(path):
            raise TypeError(f'{path!r} is not a valid file.')
        elif not os.access(path, os.R_OK):
            raise PermissionError(f'I do not have read access to {path!r}.')
        else:
            self.path = path
            self.__value = None
            self.deserializer = deserializer

    async def async_get(self):
        """Asynchronously reads the config from file."""
        if self.__value is not None:
            return self.__value
        else:
            async with aiofiles.open(self.path) as fp:
                with io.StringIO(await fp.read()) as str_io:
                    str_io.seek(0)

                    is_coro = asyncio.iscoroutine(self.deserializer)
                    is_coro_fn = asyncio.iscoroutinefunction(self.deserializer)

                    if is_coro or is_coro_fn:
                        return await self.deserializer(str_io)
                    else:
                        return self.deserializer(str_io)

    def sync_get(self):
        """Blocks while we read the config from the file."""
        if self.__value is not None:
            return self.__value
        else:
            with open(self.path) as fp:
                return self.deserializer(fp)

    def __await__(self):
        """Returns the awaitable returned by async_get"""
        return self.async_get()

    __call__ = sync_get

    def invalidate(self):
        """
        Invalidates the cache. This causes the next read to cause a new file
        read operation.
        """
        old = self.__value
        self.__value = None
        return old

    @property
    def is_cached(self):
        return self.__value is not None


def get_config_data(file_name, *, deserializer=None):
    """
    Reads the config file from the default configuration directory.

    :param file_name: the file to open in the configuration directory.
    :param deserializer: the deserialization method to use.
    :returns: a ConfigFile object.
    """
    path = os.path.join(CONFIG_DIRECTORY, file_name)
    if deserializer is not None:
        return ConfigFile(path, deserializer=deserializer)
    else:
        return ConfigFile(path)
